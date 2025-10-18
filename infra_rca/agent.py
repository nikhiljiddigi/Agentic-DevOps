"""
AgenticInfraRCA
---------------
Entity-agnostic Infra RCA agent using Gemini reasoning via InfraRCAHelper.
Analyzes Pods, Nodes, Deployments, Services, etc.
Collects describe/events/logs/metrics → runs Gemini RCA → outputs Markdown.
"""

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from utils.k8s_helper import K8sHelper
from utils.metrics_client import MetricsClient
from utils.markdown_helper import build_markdown_generic
from utils.dspy_helper import InfraRCAHelper 


class AgenticInfraRCA:
    def __init__(self, max_workers: int = 6):
        self.k8s = K8sHelper()
        self.metrics = MetricsClient()
        self.rca = InfraRCAHelper()
        self.max_workers = max_workers

    # ------------------------------------------------------------------ #
    # Generic signal extractor (shared across all resource types)
    # ------------------------------------------------------------------ #
    def extract_signals(self, data: dict) -> str:
        """Extract common failure patterns from describe/events/logs."""
        text = " ".join(data.values()).lower()
        patterns = {
            "crashloopbackoff": "CrashLoopBackOff",
            "back-off restarting": "CrashLoopBackOff",
            "imagepullbackoff": "ImagePullBackOff",
            "failed to pull image": "ImagePullBackOff",
            "errimagepull": "ImagePullBackOff",
            "oomkilled": "OOMKilled",
            "memorypressure": "NodeMemoryPressure",
            "diskpressure": "NodeDiskPressure",
            "failedscheduling": "FailedScheduling",
            "unschedulable": "FailedScheduling",
            "evicted": "Evicted",
            "node not ready": "NodeNotReady",
            "dns": "DNSIssue",
            "readinessprobe failed": "ProbeFailure",
            "livenessprobe failed": "ProbeFailure",
            "no such host": "DNSIssue",
            "progressdeadlineexceeded": "FailedRollout",
            "unavailable": "UnavailableReplicas",
            "connection refused": "ServiceUnavailable",
            "timeout": "TimeoutError",
            "pod has unbound immediate persistentvolumeclaims": "PVCUnbound",
        }
        signals = {v for k, v in patterns.items() if k in text}
        if not signals and any(tok in text for tok in ("error", "fail", "exception", "critical")):
            signals.add("GeneralError")
        return ", ".join(sorted(signals)) if signals else "None"

    # ------------------------------------------------------------------ #
    # Analyze a single resource
    # ------------------------------------------------------------------ #
    def analyze_resource(self, kind: str, name: str, namespace: str = None):
        """
        Collect K8s data, extract signals, run RCA reasoning and return structured result.

        Returns:
            None when nothing to analyze (empty resource),
            otherwise a dict:
            {
                "kind": kind,
                "name": name,
                "namespace": namespace,
                "root_cause": "...",
                "reasoning": "...",
                "recommendations": [...],
                "patch_yaml": "...",
                "category": "...",
                "markdown": "full md report"
            }
        """
        # 1) Collect K8s resource data
        data = self.k8s.collect_resource_data(kind, name, namespace)

        # skip empty resources
        if not data or not any((v or "").strip() for v in data.values()):
            # nothing to analyze
            return None

        # 2) Summarize metrics depending on resource kind
        if kind.lower() in ("pod", "deployment", "replicaset", "statefulset"):
            metrics_summary = self.metrics.summarize_pod(namespace or "default", name)
        else:
            metrics_summary = self.metrics.summarize_nodes()

        # 3) Extract signals
        signals = self.extract_signals(data)

        # 4) Run RCA reasoning (LLM)
        diag = {}
        try:
            diag = self.rca.run_rca(
                kind=kind,
                name=name,
                namespace=namespace or "",
                describe=data.get("describe", ""),
                events=data.get("events", ""),
                logs=data.get("logs", ""),
                metrics=metrics_summary,
                signals=signals,
            ) or {}
        except Exception as e:
            # Ensure diag is a dict even on error
            print(f"❌ Error running RCA for {kind}/{name}: {e}")
            diag = {}

        # 5) Extract fields safely with defaults
        root_cause = (diag.get("root_cause") or "").strip()
        reasoning = (diag.get("reasoning") or "").strip()
        recommendations = diag.get("recommendations") or []
        patch_yaml = (diag.get("patch_yaml") or "").strip()
        category = (diag.get("category") or "").strip() or "General Anomaly"

        # --- fallback text for empty or trivial output ---
        if not root_cause or len(root_cause) < 5:
            root_cause = "Root cause not identifiable"
        if not reasoning or len(reasoning) < 20:
            reasoning = (
                f"No sufficient diagnostic context for {kind} `{name}` "
                f"in namespace `{namespace or 'default'}`. "
                f"Detected signals: {signals}. "
                "Possible transient or resolved condition."
            )
        if not recommendations:
            recommendations = [f"No specific remediation identified for {kind} `{name}`."]

        # --- Context-aware patch decision ---
        if not patch_yaml or patch_yaml.lower() in ("# none", "none") or len(patch_yaml.strip()) < 5:
            if kind.lower() in ("node", "service", "persistentvolume", "pvc"):
                patch_yaml = ""  # these resources don't have manifest patches
            else:
                patch_yaml = "# No manifest change required."

        # 6) Build markdown report
        md = build_markdown_generic(kind, name, namespace, root_cause, reasoning, recommendations, patch_yaml, category)

        # 7) Build and return full structured result
        result = {
            "kind": kind,
            "name": name,
            "namespace": namespace,
            "root_cause": root_cause,
            "reasoning": reasoning,
            "recommendations": recommendations,
            "patch_yaml": patch_yaml,
            "category": category,
            "markdown": md,
        }

        return result


    # ------------------------------------------------------------------ #
    # Cluster-wide RCA (async, entity-agnostic)
    # ------------------------------------------------------------------ #
    async def analyze_cluster(self, exclude_system=True, kinds=None):
        """Scan cluster and analyze resources concurrently."""
        if kinds is None:
            kinds = ["Pod", "Node", "Deployment", "Service"]

        namespaces = self.k8s.list_namespaces(exclude_system)
        if not namespaces:
            print("⚪ No namespaces found — cluster may be empty.")
            return ""

        resources = []
        for kind in kinds:
            if kind.lower() == "node":
                for n in self.k8s.list_resources("node"):
                    resources.append(("Node", n, None))
                continue

            for ns in namespaces:
                names = self.k8s.list_resources(kind, ns)
                if not names:
                    continue  # skip empty namespaces
                for name in names:
                    resources.append((kind, name, ns))

        if not resources:
            print("⚪ No analyzable resources found.")
            return ""

        print("\n📊 Cluster Node Metrics:\n" + self.metrics.summarize_nodes() + "\n")

        loop = asyncio.get_event_loop()
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            tasks = [loop.run_in_executor(pool, self.analyze_resource, k, n, ns) for k, n, ns in resources]
            for res in await asyncio.gather(*tasks, return_exceptions=True):
                if isinstance(res, Exception):
                    results.append({"markdown": f"# ⚠️ Analyzer error: {res}"})
                elif res is not None:
                    results.append(res)

        report_parts = [r["markdown"] for r in results if "markdown" in r]
        if not report_parts:
            print("⚪ No meaningful RCA output generated.")
            return ""

        final = "\n\n-------------------------------------------------------\n\n".join(report_parts)
        with open("cluster_rca_report.md", "w") as f:
            f.write(final)
        print("✅ RCA complete. Saved → cluster_rca_report.md")
        return final
