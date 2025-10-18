import os
import subprocess
import requests

class MetricsClient:
    """Lightweight metrics client: prefer kubectl top; optional Prometheus if PROM_URL set."""

    def __init__(self):
        self.prom_url = os.getenv("PROM_URL")

    def summarize_nodes(self):
        """Return a short textual summary of node CPU/memory."""
        if self.prom_url:
            # example simple query: node CPU usage in cores (instant)
            try:
                q = 'sum by (instance) (rate(node_cpu_seconds_total[5m]))'
                resp = requests.get(f"{self.prom_url}/api/v1/query", params={"query": q}, timeout=5)
                j = resp.json()
                lines = []
                for r in j.get("data", {}).get("result", []):
                    inst = r.get("metric", {}).get("instance", "unknown")
                    val = r.get("value", ["", ""])[1]
                    lines.append(f"{inst}: cpu_rate={val}")
                return "\n".join(lines) if lines else "No prometheus node metrics"
            except Exception:
                pass

        # fallback to kubectl top
        out = subprocess.getoutput("kubectl top nodes --no-headers 2>/dev/null || echo 'metrics unavailable'")
        lines = []
        for l in out.splitlines():
            if l.strip():
                parts = l.split()
                if len(parts) >= 3:
                    lines.append(f"{parts[0]}: CPU {parts[1]}, Memory {parts[2]}")
        return "\n".join(lines) if lines else "No node metrics available"

    def summarize_pod(self, namespace, pod):
        out = subprocess.getoutput(f"kubectl top pod {pod} -n {namespace} --no-headers 2>/dev/null || echo 'metrics unavailable'")
        return out.strip()
