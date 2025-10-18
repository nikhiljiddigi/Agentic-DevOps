import os
import time
import json
import traceback
import threading
from datetime import datetime
from kubernetes import client, config, watch
from agent import AgenticInfraRCA
from threading import Lock

# ===============================================================
# 🔧 Global Locks & Persistent Cooldown Cache
# ===============================================================
rca_lock = Lock()
CACHE_FILE = "rca_seen_cache.json"
RCA_COOLDOWN = 300  # 5 minutes

def load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_cache():
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(last_rca_time, f)
    except Exception as e:
        print(f"⚠️ Failed to save RCA cache: {e}")

# load cache on start
last_rca_time = load_cache()

# ===============================================================
# ✅ Kubernetes Connection
# ===============================================================
try:
    config.load_kube_config()
except Exception:
    config.load_incluster_config()

# ===============================================================
# ✅ Prepare Directories and Agent
# ===============================================================
os.makedirs("rca_reports", exist_ok=True)
agent = AgenticInfraRCA()

RCA_TRIGGERS = [
    "CrashLoopBackOff",
    "ImagePullBackOff",
    "ErrImagePull",
    "OOMKilled",
    "FailedScheduling",
    "BackOff",
    "ProbeError",
    "Unhealthy",
]

# ===============================================================
# 🧠 Reusable Helper Functions
# ===============================================================
def should_skip_rca(kind, name, ns):
    """Check cooldown cache to prevent duplicate RCAs."""
    key = f"{kind}:{name}:{ns}"
    now = time.time()
    if key in last_rca_time and now - last_rca_time[key] < RCA_COOLDOWN:
        print(f"⏳ Skipping duplicate RCA for {key} (cooldown active).")
        return True
    last_rca_time[key] = now
    save_cache()
    return False


def trigger_rca(kind, name, ns, category="General Anomaly", prefix="event"):
    """Centralized RCA execution, locking, and saving."""
    try:
        if should_skip_rca(kind, name, ns):
            return

        with rca_lock:
            result = agent.analyze_resource(kind=kind, name=name, namespace=ns)

        if not result:
            print(f"⚠️ No data found for {kind}/{name}, skipping RCA.")
            return

        print(f"🧩 RCA Fields: RootCause='{result.get('root_cause','')[:60]}', "
              f"Reasoning='{result.get('reasoning','')[:60]}', "
              f"Category='{result.get('category','')}.'")

        save_rca_report(kind, name, ns, result, category=result.get("category", category), prefix=prefix)

    except Exception as e:
        print(f"❌ RCA execution failed for {kind}/{name}: {e}")
        traceback.print_exc()


def save_rca_report(kind, name, ns, result, category="General Anomaly", prefix="event"):
    """Safely save RCA output (dict or markdown) as .md file."""
    from utils.markdown_helper import build_markdown_generic

    try:
        if isinstance(result, dict):
            result = build_markdown_generic(
                kind=kind,
                name=name,
                namespace=ns,
                root_cause=result.get("root_cause", ""),
                reasoning=result.get("reasoning", ""),
                recommendations=result.get("recommendations", []),
                patch_yaml=result.get("patch_yaml", ""),
                category=result.get("category", category),
            )
        elif not isinstance(result, str):
            result = str(result)

        safe_kind = kind.replace("/", "_")
        safe_ns = ns or "default"
        filename = f"{prefix}_{safe_kind}_{name}_{safe_ns}.md"
        file_path = os.path.join("rca_reports", filename)

        with open(file_path, "w") as f:
            f.write(result)

        print(f"✅ RCA saved → {file_path}")
        return file_path

    except Exception as e:
        print(f"❌ Failed to save RCA report for {kind}/{name}: {e}")
        traceback.print_exc()


# ===============================================================
# 👀 Event Watcher
# ===============================================================
def watch_cluster_events():
    v1 = client.CoreV1Api()
    w = watch.Watch()
    print("👀 Starting event watcher (Agentic RCA Mode)...")

    while True:
        try:
            for evt in w.stream(v1.list_event_for_all_namespaces, timeout_seconds=60):
                event_obj = evt["object"]
                reason = getattr(event_obj, "reason", "")
                if any(t in reason for t in RCA_TRIGGERS):
                    involved = event_obj.involved_object
                    kind = involved.kind
                    ns = involved.namespace or "default"
                    name = involved.name
                    print(f"\n⚡ Detected issue [{reason}] on {kind}/{name} in ns={ns}")
                    trigger_rca(kind, name, ns, category="Event Anomaly", prefix="event")

        except Exception as e:
            print(f"⚠️ Watch error: {e}. Restarting watcher in 5s...")
            time.sleep(5)
            continue


# ===============================================================
# 📊 Metrics Watcher
# ===============================================================
def watch_metrics(cpu_threshold=80, mem_threshold=80, interval=30):
    metrics_api = client.CustomObjectsApi()
    print("📈 Starting metrics watcher...")

    while True:
        try:
            data = metrics_api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")

            for item in data["items"]:
                kind = "Node"
                ns = ""
                name = item["metadata"]["name"]
                cpu_raw = item["usage"]["cpu"]
                mem_raw = item["usage"]["memory"]

                # crude conversion (milli CPU, Mi)
                cpu_m = int(cpu_raw.replace("n", "")) / 1e6 if "n" in cpu_raw else int(cpu_raw.replace("m", ""))
                mem_mi = int(mem_raw.replace("Ki", "")) / 1024

                if cpu_m > cpu_threshold * 10 or mem_mi > mem_threshold * 10:
                    print(f"⚠️ Node {name} CPU={cpu_m}m, Memory={mem_mi}Mi > threshold")
                    trigger_rca(kind, name, ns, category="Metrics Anomaly", prefix="metrics")

            time.sleep(interval)

        except Exception as e:
            print(f"⚠️ Metric watcher error: {e}")
            time.sleep(10)


# ===============================================================
# 🐳 Pod Status Watcher
# ===============================================================

def watch_pod_statuses(interval=20):
    """Continuously scan for pods terminated due to OOMKilled or similar conditions."""
    v1 = client.CoreV1Api()
    print("🔍 Starting pod status watcher (for OOMKilled, CrashLoopBackOff, PodFailed)...")

    while True:
        try:
            pods = v1.list_pod_for_all_namespaces(watch=False).items

            for pod in pods:
                ns = pod.metadata.namespace
                name = pod.metadata.name
                kind = "Pod"
                conditions = pod.status.conditions or []
                statuses = pod.status.container_statuses or []

                # --- 1️⃣ Detect OOMKilled ---
                for cs in statuses:
                    if cs.state and cs.state.terminated:
                        reason = cs.state.terminated.reason
                        exit_code = cs.state.terminated.exit_code
                        if reason == "OOMKilled" or exit_code == 137:
                            print(f"⚡ OOMKilled detected for {kind}/{name} in ns={ns} (exitCode={exit_code})")
                            trigger_rca(kind, name, ns, category="Resource Pressure", prefix="event")

                # --- 2️⃣ Detect PodFailed / NotReady containers ---
                for cond in conditions:
                    if cond.type in ["Ready", "ContainersReady"] and cond.status == "False":
                        reason = getattr(cond, "reason", "")
                        if reason in ["PodFailed", "CrashLoopBackOff"]:
                            print(f"⚡ Pod failure condition [{reason}] for {kind}/{name} in ns={ns}")
                            trigger_rca(kind, name, ns, category="Application Failure", prefix="event")

            time.sleep(interval)

        except Exception as e:
            print(f"⚠️ Pod status watcher error: {e}")
            time.sleep(10)


# ===============================================================
# 🚀 Entry Point
# ===============================================================
if __name__ == "__main__":
    t1 = threading.Thread(target=watch_cluster_events)
    t2 = threading.Thread(target=watch_metrics)
    t3 = threading.Thread(target=watch_pod_statuses)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
