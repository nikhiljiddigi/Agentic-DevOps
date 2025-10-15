import os
import dspy
from dspy import Prediction
from shared.config import configure_lm
from shared.mcp_client import MockMCPClient


class PreDeployAgent(dspy.Module):
    """Agent to validate deployment manifests before rollout."""

    def __init__(self, mcp_client):
        super().__init__()
        self.mcp_client = mcp_client

        # LLM-powered validation of manifests
        self.validate_manifest = dspy.Predict(
            "manifest_yaml -> warnings: list[str], root_warning: str, risk_score: float, recommendations: list[str]"
        )

    def forward(self, manifest_path: str) -> Prediction:
        """Analyze deployment manifest for risky configurations."""
        # Load manifest YAML
        with open(manifest_path, "r") as f:
            manifest = f.read()

        result = self.validate_manifest(manifest_yaml=manifest)

        # Fallbacks in case some fields are missing
        warnings = getattr(result, "warnings", []) or ["No warnings found."]
        root_warning = getattr(result, "root_warning", "No critical warning detected.")
        risk_score = getattr(result, "risk_score", 0.0)
        recommendations = getattr(result, "recommendations", []) or ["No recommendations provided."]

        return dspy.Prediction(
            warnings=warnings,
            root_warning=root_warning,
            risk_score=risk_score,
            recommendations=recommendations
        )


def run_config_agent():
    configure_lm()
    mcp_client = MockMCPClient()
    agent = PreDeployAgent(mcp_client)

    manifest_path = os.path.join(os.path.dirname(__file__), "sample_manifest.yaml")
    result = agent(manifest_path)

    print("\n✅ Pre-Deploy Validation Results:")
    print("Warnings:")
    for w in result.warnings:
        print(f"  - {w}")

    print(f"\n🔥 Root Warning: {result.root_warning}")
    print(f"\n⚖️  Risk Score: {result.risk_score:.2f}")

    print("\n🩺 Recommendations:")
    for r in result.recommendations:
        print(f"  - {r}")


if __name__ == "__main__":
    run_config_agent()
