import os
import dspy
from dspy import Prediction
from shared.config import configure_lm
from shared.mcp_client import MockMCPClient


class CICDLogAgent(dspy.Module):
    """Agent to analyze CI/CD pipeline logs and suggest fixes."""

    def __init__(self, mcp_client):
        super().__init__()
        self.mcp_client = mcp_client

        # Step 1 → detect root cause + suggestions
        self.analyze_failure = dspy.Predict(
            "pipeline_logs -> root_cause: str, fix_suggestions: list[str]"
        )

        # Step 2 → estimate severity of impact
        self.impact_estimate = dspy.Predict(
            "root_cause -> impact_level: str"
        )

    def forward(self, pipeline_id: str) -> Prediction:
        """Fetch logs and run failure analysis."""
        print(f"\n🔍 Running CI/CD Failure Analysis for: {pipeline_id}")

        # Fetch mock logs
        with open(os.path.join(os.path.dirname(__file__), "sample_logs.txt")) as f:
            logs = f.read()

        # Run predictors
        analysis = self.analyze_failure(pipeline_logs=logs)
        impact = self.impact_estimate(root_cause=analysis.root_cause)

        return dspy.Prediction(
            root_cause=analysis.root_cause,
            fix_suggestions=analysis.fix_suggestions,
            impact_level=impact.impact_level
        )


def run_cicd_agent():
    configure_lm()
    mcp_client = MockMCPClient()
    agent = CICDLogAgent(mcp_client)

    result = agent("demo-pipeline-001")

    print(f"Root Cause: {result.root_cause}")
    print("Fix Suggestions:")
    for s in result.fix_suggestions:
        print(f"  - {s}")
    print(f"Impact Level: {result.impact_level}")


if __name__ == "__main__":
    run_cicd_agent()
