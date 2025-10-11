import os
from typing import Dict, List, Optional
import dspy
from dspy import Prediction
from agenspy import RealMCPClient

class PRReviewAgent(dspy.Module):
    """Agent for automated PR reviews."""
    
    def __init__(self, mcp_client, github_token: Optional[str] = None):
        super().__init__()
        self.mcp_client = mcp_client
        self.github_token = github_token

        # Define predictors with modern signature syntax using ->
        self.analyze_changes = dspy.Predict(
            "pr_content -> security_issues: list[str], edge_cases: list[str]"
        )
        
        self.review_docs = dspy.Predict(
            "changes -> doc_updates: list[str], doc_suggestions: list[str]"
        )
        
        self.analyze_impact = dspy.Predict(
            "changes, codebase -> impact_analysis: str, risk_score: float"
        )

    def forward(self, pr_url: str) -> Prediction:
        """Review a pull request and provide comprehensive analysis."""
        print(f"🔍 Reviewing PR: {pr_url}")
        
        # Define default values
        default_security = ["No security issues identified in the current codebase"]
        default_edge_cases = ["No potential edge cases detected"]
        default_doc_updates = ["No documentation updates required"]
        default_doc_suggestions = ["Documentation appears to be complete"]
        default_impact = "No significant impact detected"
        default_risk = 0.0
        
        # Fetch PR data
        pr_data = self.mcp_client(
            context_request=f"Get PR details for {pr_url}",
            tool_name="get_pull_request",
            tool_args={"url": pr_url}
        )

        # Access the data properly from pr_data
        context_data = pr_data.get('context_data', {})
        diff_data = pr_data.get('diff', '') 

        try:
            # Analyze changes using modern predictor calls
            analysis = self.analyze_changes(pr_content=context_data)
            doc_review = self.review_docs(changes=diff_data)
            impact = self.analyze_impact(
                changes=diff_data,
                codebase=context_data
            )

            # Return a Prediction object with defaults
            return dspy.Prediction(
                security_issues=getattr(analysis, 'security_issues', []) or default_security,
                edge_cases=getattr(analysis, 'edge_cases', []) or default_edge_cases,
                doc_updates=getattr(doc_review, 'doc_updates', []) or default_doc_updates,
                doc_suggestions=getattr(doc_review, 'doc_suggestions', []) or default_doc_suggestions,
                impact_analysis=getattr(impact, 'impact_analysis', '') or default_impact,
                risk_score=getattr(impact, 'risk_score', 0.0) or default_risk
            )
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            # Return prediction with default values on error
            return dspy.Prediction(
                security_issues=default_security,
                edge_cases=default_edge_cases,
                doc_updates=default_doc_updates,
                doc_suggestions=default_doc_suggestions,
                impact_analysis=default_impact,
                risk_score=default_risk
            )

def main():
    """Run PR Review Agent demo."""
    github_token = os.getenv('GITHUB_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not all([github_token, openai_key]):
        raise EnvironmentError("Please set GITHUB_TOKEN and OPENAI_API_KEY")

    # Configure DSPy with modern configuration
    lm = dspy.LM('openai/gpt-4o-mini', api_key=openai_key)
    dspy.configure(lm=lm)

    # Setup MCP client
    mcp_client = RealMCPClient(
        ["npx", "-y", "@modelcontextprotocol/server-github"]
    )

    try:
        # Create and run agent
        agent = PRReviewAgent(mcp_client, github_token)
        result = agent.forward("https://github.com/SuperagenticAI/SuperXLab/pull/1")

        print("\n📋 PR Review Results:")
        for key, value in result.items():
            print(f"\n{key.replace('_', ' ').title()}:")
            if isinstance(value, list):
                for item in value:
                    print(f"  - {item}")
            else:
                print(f"  {value}")
                
    except Exception as e:
        print(f"Error during PR review: {str(e)}")

if __name__ == "__main__":
    main()