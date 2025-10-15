import os
import json
import dspy
from dspy import Prediction
from shared.config import configure_lm
from shared.mcp_client import MockMCPClient


class InfraRCAGeneratorAgent(dspy.Module):
    """Agent to generate infrastructure-level RCA summaries."""

    def __init__(self, mcp_client):
        super().__init__()
        self.mcp_client = mcp_client

        # Predictor for infra incident context
        self.generate_rca = dspy.Predict(
            "infra_context -> root_cause: str, affected_components: list[str], impact_summary: str, resolution_steps: list[str], prevention_steps: list[str]"
        )

    def forward(self, incident_path: str) -> Prediction:

        with open(incident_path, "r") as f:
            context = json.load(f)

        result = self.generate_rca(infra_context=json.dumps(context))

        # Fallbacks
        root_cause = getattr(result, "root_cause", "Unable to determine root cause.")
        affected_components = getattr(result, "affected_components", []) or ["Unknown"]
        impact_summary = getattr(result, "impact_summary", "Impact not determined.")
        resolution_steps = getattr(result, "resolution_steps", []) or ["No resolution steps provided."]
        prevention_steps = getattr(result, "prevention_steps", []) or ["No prevention steps provided."]

        return dspy.Prediction(
            root_cause=root_cause,
            affected_components=affected_components,
            impact_summary=impact_summary,
            resolution_steps=resolution_steps,
            prevention_steps=prevention_steps
        )


def run_rca_agent():
    configure_lm()
    mcp_client = MockMCPClient()
    agent = InfraRCAGeneratorAgent(mcp_client)

    incident_path = os.path.join(os.path.dirname(__file__), "sample_alerts.json")
    result = agent(incident_path)

    print("\n✅ Infra RCA Summary Report:")
    print(f"\n🔥 Root Cause: {result.root_cause}")
    print("\n🧩 Affected Components:")
    for c in result.affected_components:
        print(f"  - {c}")
    print(f"\n💥 Impact Summary: {result.impact_summary}")

    print("\n🩺 Resolution Steps:")
    for r in result.resolution_steps:
        print(f"  - {r}")

    # print("\n🛡️ Prevention Steps:")
    # for p in result.prevention_steps:
    #     print(f"  - {p}")


if __name__ == "__main__":
    run_rca_agent()
