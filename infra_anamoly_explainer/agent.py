import os
import json

THRESHOLDS = {
    "cpu": 85,
    "memory": 85,
    "latency_ms": 200,
    "pod_restarts": 3
}

def load_metrics(file_path):
    with open(file_path) as f:
        return json.load(f)

def detect_anomalies(metrics):
    findings = []
    if metrics.get("cpu", 0) > THRESHOLDS["cpu"]:
        findings.append(f"CPU usage {metrics['cpu']}% exceeds {THRESHOLDS['cpu']}%")
    if metrics.get("memory", 0) > THRESHOLDS["memory"]:
        findings.append(f"Memory usage {metrics['memory']}% exceeds {THRESHOLDS['memory']}%")
    if metrics.get("latency_ms", 0) > THRESHOLDS["latency_ms"]:
        findings.append(f"High latency {metrics['latency_ms']} ms")
    if metrics.get("pod_restarts", 0) > THRESHOLDS["pod_restarts"]:
        findings.append(f"{metrics['pod_restarts']} pod restarts detected")
    return findings

def interpret(findings, metrics):
    if not findings:
        return ("Healthy", "System metrics are within normal thresholds.",
                ["Continue monitoring periodically."])
    causes, recos = [], []
    if "CPU" in " ".join(findings):
        causes.append("Possible high workload or tight loop.")
        recos.append("Check top CPU pods; consider HPA scaling.")
    if "Memory" in " ".join(findings):
        causes.append("Memory leak or unbounded cache growth.")
        recos.append("Review memory limits; restart leaking pods.")
    if "latency" in " ".join(findings):
        causes.append("Network congestion or backend slowdown.")
        recos.append("Check downstream service response times.")
    if "pod restarts" in " ".join(findings):
        causes.append("CrashLoop or readiness probe failures.")
        recos.append("Inspect pod logs and readiness config.")
    return ("Unhealthy", " | ".join(causes), recos)

def main():
    base = os.path.dirname(__file__)
    metrics_file = os.path.join(base, "sample_metrics.json")
    metrics = load_metrics(metrics_file)

    # print(f"\n🔍 Analyzing metrics from: {metrics_file}")
    # print(json.dumps(metrics, indent=2))

    findings = detect_anomalies(metrics)
    print("\n✅ Anomaly Report:")
    if not findings:
        print("  All metrics OK.")
    else:
        for f in findings:
            print(f"  - {f}")

    status, explanation, recos = interpret(findings, metrics)

    print(f"\n🧠 Status: {status}")
    print(f"📖 Explanation: {explanation}")
    print("\n🩺 Recommendations:")
    for r in recos:
        print(f"  - {r}")

if __name__ == "__main__":
    main()
