import subprocess
from kubernetes import client, config
import urllib3
from kubernetes.client import Configuration, ApiClient

class K8sHelper:
    """Kubernetes helper: connect via API (in-cluster or kubeconfig) with fallback (kubectl)."""

    def __init__(self, skip_tls_on_fail=True):
        self.v1 = None
        self.core = None
        self.skip_tls_on_fail = skip_tls_on_fail
        self._connect_to_k8s()

    def _connect_to_k8s(self):
        # Try in-cluster first
        try:
            config.load_incluster_config()
            self.v1 = client.CoreV1Api()
            self.core = self.v1
            return
        except Exception:
            pass

        # Try normal kubeconfig
        try:
            config.load_kube_config()
            self.v1 = client.CoreV1Api()
            self.core = self.v1
            # probe
            self.v1.list_namespace(_request_timeout=5)
            return
        except Exception as e:
            print(f"⚠️ API access failed: {e}")

        # Optionally retry with skip-TLS for self-signed certs (K3s typical)
        if self.skip_tls_on_fail:
            try:
                print("🔧 Retrying connection with skip-TLS (insecure) ...")
                urllib3.disable_warnings()
                c = Configuration()
                config.load_kube_config(client_configuration=c)
                c.verify_ssl = False
                c.assert_hostname = False
                ApiClient(configuration=c)  # ensure configuration applied
                self.v1 = client.CoreV1Api(ApiClient(c))
                self.core = self.v1
                # probe
                self.v1.list_namespace(_request_timeout=5)
                return
            except Exception as e2:
                print(f"❌ Failed to connect with skip-TLS: {e2}")

        # if all fails, fallback to None and rely on kubectl subprocess calls
        self.v1 = None
        print("⚠️ Falling back to kubectl subprocess for data collection.")

    # -------------------------
    # Namespace & resource listing
    # -------------------------
    def list_namespaces(self, exclude_system=True):
        if self.v1:
            try:
                ns_objs = self.v1.list_namespace().items
                namespaces = [ns.metadata.name for ns in ns_objs]
            except Exception as e:
                print(f"⚠️ Error fetching namespaces via API: {e}")
                namespaces = []
        else:
            out = subprocess.getoutput("kubectl get ns --no-headers -o custom-columns=NAME:.metadata.name")
            namespaces = [l.strip() for l in out.splitlines() if l.strip()]

        if exclude_system:
            skip = {"kube-system", "kube-public", "kube-node-lease", "monitoring"}
            namespaces = [n for n in namespaces if n not in skip]
        return namespaces

    def list_resources(self, kind: str, namespace: str = None):
        """
        Return a list of resource names for a given kind in a namespace (if provided).
        kind examples: pod, node, deployment, service, daemonset, replicasets
        """
        kind_lower = kind.lower()
        if kind_lower == "node":
            if self.v1:
                try:
                    nodes = self.v1.list_node().items
                    return [n.metadata.name for n in nodes]
                except Exception:
                    pass
            out = subprocess.getoutput("kubectl get nodes --no-headers | awk '{print $1}'")
            return [l.strip() for l in out.splitlines() if l.strip()]

        # For namespaced kinds:
        ns_flag = f"-n {namespace}" if namespace else "-A"
        try:
            out = subprocess.getoutput(f"kubectl get {kind_lower} {ns_flag} --no-headers -o custom-columns=KIND:.kind,NAME:.metadata.name,NAMESPACE:.metadata.namespace")
            lines = [l for l in out.splitlines() if l.strip()]
            # return tuples (name, namespace) when ns provided, else list of names
            if namespace:
                return [l.split()[1] for l in lines]
            else:
                # parse names with their namespaces
                return [ (parts[1], parts[2]) for parts in (ln.split() for ln in lines) ]
        except Exception:
            return []

    # -------------------------
    # Generic resource data collection (entity-agnostic)
    # -------------------------
    def collect_resource_data(self, kind: str, name: str, namespace: str = None):
        """
        Collect describe, events, logs (if pod), metrics (kubectl top fallback).
        Returns dict with keys: describe, events, logs, metrics
        """
        describe = ""
        events = ""
        logs = ""
        metrics = ""

        # Prefer API when possible for structured data
        if self.v1:
            try:
                if kind.lower() == "pod":
                    pod_obj = self.v1.read_namespaced_pod(name, namespace)
                    describe = pod_obj.to_str()
                elif kind.lower() == "node":
                    node_obj = self.v1.read_node(name)
                    describe = node_obj.to_str()
                else:
                    # for deployments/services, use kubectl describe for readability
                    describe = subprocess.getoutput(f"kubectl describe {kind} {name} -n {namespace}") if namespace else subprocess.getoutput(f"kubectl describe {kind} {name}")
            except Exception:
                # fallback to kubectl describe text
                ns_flag = f"-n {namespace}" if namespace else ""
                describe = subprocess.getoutput(f"kubectl describe {kind} {name} {ns_flag}")

            # Events via API filtering
            try:
                evs = self.v1.list_namespaced_event(namespace) if namespace else self.v1.list_event_for_all_namespaces()
                pod_events = []
                for e in evs.items:
                    obj = e.involved_object
                    if obj and obj.name == name and (not namespace or obj.namespace == namespace):
                        ts = getattr(e, "last_timestamp", None) or getattr(e, "event_time", None) or ""
                        pod_events.append(f"{ts} {e.type} {e.reason}: {e.message}")
                events = "\n".join(pod_events)
            except Exception:
                ns_flag = f"-n {namespace}" if namespace else ""
                events = subprocess.getoutput(f"kubectl get events {ns_flag} --field-selector involvedObject.name={name} -o wide")
            # logs only for pods
            if kind.lower() == "pod":
                try:
                    logs = self.v1.read_namespaced_pod_log(name, namespace, tail_lines=200)
                except Exception:
                    logs = subprocess.getoutput(f"kubectl logs {name} -n {namespace} --tail=200 2>/dev/null || true")
        else:
            # cli-only fallback
            ns_flag = f"-n {namespace}" if namespace else ""
            describe = subprocess.getoutput(f"kubectl describe {kind} {name} {ns_flag} 2>/dev/null || true")
            events = subprocess.getoutput(f"kubectl get events {ns_flag} --field-selector involvedObject.name={name} -o wide 2>/dev/null || true")
            if kind.lower() == "pod":
                logs = subprocess.getoutput(f"kubectl logs {name} -n {namespace} --tail=200 2>/dev/null || true")

        # metrics (kubectl top) — apply namespace for pods
        try:
            if kind.lower() == "pod":
                metrics = subprocess.getoutput(f"kubectl top pod {name} -n {namespace} --no-headers 2>/dev/null || echo 'metrics unavailable'")
            elif kind.lower() == "node":
                metrics = subprocess.getoutput(f"kubectl top node {name} --no-headers 2>/dev/null || echo 'metrics unavailable'")
            else:
                metrics = "metrics unavailable"
        except Exception:
            metrics = "metrics unavailable"

        return {"describe": describe or "", "events": events or "", "logs": logs or "", "metrics": metrics or ""}
