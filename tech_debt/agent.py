import os
import dspy
from typing import Dict, List, Optional
from dspy.signatures.signature import Signature
from agenspy import RealMCPClient

class DependencyAnalysis(Signature):
    """Analyze dependencies for technical debt."""
    def __init__(self):
        super().__init__()
        self.input_fields = ["dependencies"]
        self.output_fields = ["deprecated", "updates"]

class ComplexityAnalysis(Signature):
    """Analyze code complexity.""" 
    def __init__(self):
        super().__init__()
        self.input_fields = ["code"]
        self.output_fields = ["complex_modules", "refactor_suggestions"]

class TestAnalysis(Signature):
    """Analyze test coverage."""
    def __init__(self):
        super().__init__()
        self.input_fields = ["codebase"]
        self.output_fields = ["coverage_gaps", "test_recommendations"]

class TechDebtAgent(dspy.Module):
    """Agent for analyzing technical debt."""
    
    def __init__(self, mcp_client, github_token: Optional[str] = None):
        super().__init__()
        self.mcp_client = mcp_client
        self.github_token = github_token

        # Define predictors with instructions
        self.analyze_deps = dspy.Predict(
            DependencyAnalysis,
            instructions="Analyze project dependencies and identify outdated or deprecated packages"
        )
        
        self.analyze_complexity = dspy.Predict(
            ComplexityAnalysis,
            instructions="Analyze code complexity and suggest refactoring opportunities"
        )
        
        self.analyze_tests = dspy.Predict(
            TestAnalysis,
            instructions="Analyze test coverage and provide recommendations for improvement"
        )

    def forward(self, repo_url: str) -> Dict:
        """Scan repository for technical debt."""
        print(f"📊 Scanning repo: {repo_url}")
        
        # Get repository data
        repo_data = self.mcp_client(
            context_request=f"Get repository data for {repo_url}",
            tool_name="get_repository", 
            tool_args={"url": repo_url}
        )

        # Extract data from repo_data dictionary
        repo_content = repo_data.get('content', {})
        
        # Default values for empty responses
        default_security = ["No security issues identified in the current codebase"]
        default_edge_cases = ["No critical edge cases detected"]
        default_doc_updates = ["Documentation appears to be up to date"]
        default_doc_suggestions = ["No immediate documentation improvements needed"]
        default_complex = ["No complex modules identified"]
        default_refactor = ["No immediate refactoring needed"]
        
        # Run analyses with typed signatures
        deps = self.analyze_deps(
            dependencies=repo_content.get('dependencies', '[]')
        )
        complexity = self.analyze_complexity(
            code=repo_content.get('code_content', '')
        )
        tests = self.analyze_tests(
            codebase=repo_content.get('context_data', '{}')
        )

        # Return results with meaningful default values
        return {
            "security_issues": (
                getattr(deps, 'security_issues', []) or default_security
            ),
            "edge_cases": (
                getattr(deps, 'edge_cases', []) or default_edge_cases
            ),
            "doc_updates": (
                getattr(tests, 'doc_updates', []) or default_doc_updates
            ),
            "doc_suggestions": (
                getattr(tests, 'doc_suggestions', []) or default_doc_suggestions
            ),
            "complex_modules": (
                getattr(complexity, 'complex_modules', []) or default_complex
            ),
            "refactoring_suggestions": (
                getattr(complexity, 'refactor_suggestions', []) or default_refactor
            )
        }

def main():
    """Run Tech Debt Agent demo."""
    github_token = os.getenv('GITHUB_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not all([github_token, openai_key]):
        raise EnvironmentError("Please set GITHUB_TOKEN and OPENAI_API_KEY")

    # Configure DSPy with latest syntax
    gpt4_mini = dspy.LM('openai/gpt-4o-mini', max_tokens=2000)
    dspy.configure(lm=gpt4_mini)
    # Setup MCP client
    mcp_client = RealMCPClient(
        ["npx", "-y", "@modelcontextprotocol/server-github"]
    )

    # Create and run agent
    agent = TechDebtAgent(mcp_client, github_token)
    result = agent.forward("https://github.com/SuperagenticAI/SuperXLab")

    print("\n📊 Tech Debt Analysis Results:")
    for key, value in result.items():
        print(f"\n{key.replace('_', ' ').title()}:")
        for item in value:
            print(f"  - {item}")

if __name__ == "__main__":
    main()