import os
import dspy
from typing import Dict, List, Optional
from datetime import datetime
from agenspy import RealMCPClient

class IncidentResponseAgent(dspy.Module):
    """Agent for automated incident response."""
    
    def __init__(self, mcp_client, github_token: Optional[str] = None):
        super().__init__()
        self.mcp_client = mcp_client
        self.github_token = github_token

        self.diagnose = dspy.ChainOfThought(
            "alert: str, logs: str -> root_cause: str, remediation_steps: list[str]"
        )
        
        self.auto_remediate = dspy.ChainOfThought(
            "diagnosis: str -> actions: list[str], success: bool"
        )
        
        self.create_report = dspy.ChainOfThought(
            "incident: str, actions: list[str], outcome: str -> report: str, severity: str"
        )

    def handle_incident(self, alert_data: Dict) -> Dict:
        """Handle an incident automatically."""
        print(f"🚨 Handling incident: {alert_data['title']}")
        
        # Get logs
        logs = self.mcp_client(
            context_request="Get relevant logs",
            tool_name="get_logs",
            tool_args={"alert_id": alert_data["id"]}
        )

        # Run diagnosis
        diagnosis = self.diagnose(
            alert=alert_data["description"],
            logs=logs.context_data
        )

        # Attempt remediation
        remediation = self.auto_remediate(diagnosis=diagnosis.root_cause)

        # Generate report
        report = self.create_report(
            incident=alert_data["description"],
            actions=remediation.actions,
            outcome="success" if remediation.success else "failed"
        )

        return {
            "root_cause": diagnosis.root_cause,
            "remediation_steps": diagnosis.remediation_steps,
            "auto_remediation_success": remediation.success,
            "actions_taken": remediation.actions,
            "incident_report": report.report,
            "severity": report.severity
        }

def main():
    """Run Incident Response Agent demo."""
    github_token = os.getenv('GITHUB_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not all([github_token, openai_key]):
        raise EnvironmentError("Please set GITHUB_TOKEN and OPENAI_API_KEY")

    # Configure DSPy
    dspy.configure(lm=dspy.LM('openai/gpt-4'))

    # Setup MCP client
    mcp_client = RealMCPClient(
        ["npx", "-y", "@modelcontextprotocol/server-github"],
        github_token=github_token
    )

    # Create and run agent
    agent = IncidentResponseAgent(mcp_client, github_token)
    
    # Mock incident
    mock_alert = {
        "id": "INC123",
        "title": "High API Latency",
        "description": "API response times exceeded 2s threshold",
        "timestamp": datetime.now().isoformat()
    }
    
    result = agent.handle_incident(mock_alert)

    print("\n🚨 Incident Response Results:")
    for key, value in result.items():
        print(f"\n{key.replace('_', ' ').title()}:")
        if isinstance(value, list):
            for item in value:
                print(f"  - {item}")
        else:
            print(f"  {value}")

if __name__ == "__main__":
    main()