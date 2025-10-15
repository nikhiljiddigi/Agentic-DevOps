# Agentic DevOps

The concept of Agentic DevOps got introduced in Microsoft Build conference 2024. Agentic DevOps is a paradigm, not a product. It's accessible to all, regardless of your tech stack or tooling. Use AI-powered tools like Cursor, Windsurf, Claude Code, Continue, Cline, or open-source models like Llama 4, Mistral, DeepSeek, Qwen. Deploy on-prem with vLLM, SGLang, or in the cloud with AWS, GCP, Azure.

# Agentic DevOps with DSPy + MCP

A comprehensive demonstration of Agentic DevOps using DSPy and Model Context Protocol (MCP). This suite includes specialized AI agents that automate DevOps workflows across the entire software development lifecycle.

## 🎯 Features

- **CI/CD Failure Explainer**: Analyzes pipeline failures and suggests remediation steps
- **Incident RCA Generator**: Generates root cause analysis for production incidents  
- **Infrastructure Anomaly Explainer**: Detects and explains infrastructure anomalies
- **PR Reviewer**: Automated code review before human review
- **Pre-Deploy Config Gate**: Validates deployment configurations before release
- **Security Vulnerability Watcher**: Monitors and analyzes security vulnerabilities
- **Tech Debt Analyzer**: Identifies and prioritizes technical debt

## 🚀 Workflow Stages

This project demonstrates a complete Agentic DevOps pipeline across three key stages:

### Stage 1: Pre-Commit (`--stage pr`)
- **PR Reviewer**: Analyzes code changes for quality, security, and best practices
- **Config Gate**: Validates deployment configurations and manifests
- **Security Watcher**: Scans for vulnerabilities and security issues

### Stage 2: Build & CI/CD (`--stage build`)  
- **CI/CD Failure Explainer**: Diagnoses build and deployment failures

### Stage 3: Post-Deploy (`--stage post`)
- **Infrastructure Anomaly Explainer**: Monitors system performance and detects anomalies
- **Incident RCA Generator**: Analyzes production incidents and generates root cause analysis
- **Tech Debt Analyzer**: Identifies technical debt and maintenance opportunities

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- OpenAI API key
- GitHub personal access token
- Mac OS X or Linux (Windows support may vary)

## 🚀 Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Clone the repository:
```bash
git clone https://github.com/superagenticai/agentic-devops.git
cd agentic-devops
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Note: The main dependencies are:
- `dspy-ai>=3.0.3` - DSPy framework for building language model pipelines
- `openai>=2.0.0` - OpenAI API client
- `python-dotenv>=0.2.0` - Environment variable management

## 🚀 Quick Start

1. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the complete workflow:**
   ```bash
   # Pre-commit stage (PR review, config validation, security scanning)
   python run_agentic_flow.py --stage pr
   
   # Build stage (CI/CD failure analysis)
   python run_agentic_flow.py --stage build
   
   # Post-deploy stage (anomaly detection, incident response, tech debt analysis)
   python run_agentic_flow.py --stage post
   ```

4. **Or run individual agents:**
   ```bash
   python cicd_failure_explainer/agent.py
   ```

That's it! The agents work with mock data by default, so you can explore their capabilities immediately.

## ⚙️ Configuration

1. Set up environment variables:

```bash
# For macOS/Linux
export OPENAI_API_KEY="your-openai-key"
export GITHUB_TOKEN="your-github-token"

# For Windows PowerShell
$env:OPENAI_API_KEY="your-openai-key"
$env:GITHUB_TOKEN="your-github-token"
```

Alternatively, create a `.env` file:
```bash
OPENAI_API_KEY=your-openai-key
GITHUB_TOKEN=your-github-token
```

## 🖥️ Running Individual Agents

### CI/CD Failure Explainer
```bash
python cicd_failure_explainer/agent.py
```
Analyzes CI/CD pipeline failures and provides:
- Root cause analysis
- Remediation suggestions
- Impact assessment

### Incident RCA Generator
```bash
python incident_rca_generator/agent.py
```
Generates comprehensive incident analysis including:
- Root cause identification
- Timeline reconstruction
- Preventive measures

### Infrastructure Anomaly Explainer
```bash
python infra_anamoly_explainer/agent.py
```
Detects and explains infrastructure issues:
- Performance anomalies
- Resource utilization patterns
- System health insights

### PR Reviewer
```bash
python pr_reviewer/agent.py
```
Automated code review providing:
- Security vulnerability detection
- Code quality analysis
- Best practices recommendations

### Pre-Deploy Config Gate
```bash
python predeploy_config_gate/agent.py
```
Validates deployment configurations:
- Configuration syntax checking
- Security policy compliance
- Resource allocation validation

### Security Vulnerability Watcher
```bash
python security_vulnerability_watcher/agent.py
```
Monitors security vulnerabilities:
- Code vulnerability scanning
- Dependency analysis
- Security recommendations

### Tech Debt Analyzer
```bash
python tech_debt/agent.py
```
Identifies technical debt:
- Code complexity analysis
- Refactoring opportunities
- Maintenance recommendations

## 📁 Project Structure

```
agentic-devops/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies  
├── run_agentic_flow.py                # Master orchestrator script
├── cicd_failure_explainer/            # CI/CD pipeline failure analysis
│   ├── agent.py
│   └── sample_logs.txt
├── incident_rca_generator/             # Incident root cause analysis
│   ├── agent.py
│   └── sample_alerts.json
├── infra_anamoly_explainer/           # Infrastructure anomaly detection
│   ├── agent.py
│   └── sample_metrics.json
├── pr_reviewer/                        # Automated code review
│   └── agent.py
├── predeploy_config_gate/             # Deployment configuration validation
│   ├── agent.py
│   └── sample_manifest.yaml
├── security_vulnerability_watcher/     # Security vulnerability monitoring
│   ├── agent.py
│   ├── requirements.txt
│   └── sample_code.py
├── shared/                            # Shared utilities
│   ├── config.py                      # DSPy configuration
│   └── mcp_client.py                  # Mock MCP client
└── tech_debt/                         # Technical debt analysis
    └── agent.py
```

## 🔑 API Keys and Permissions

### OpenAI API Key
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Copy and set as `OPENAI_API_KEY`

### GitHub Token (Optional)
For agents that integrate with GitHub repositories:
1. Visit [GitHub Settings > Developer Settings](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Select scopes:
   - `repo` (full access)
   - `read:org`
   - `workflow`
4. Copy and set as `GITHUB_TOKEN`

Note: Most agents work with mock data and don't require a GitHub token for basic functionality.


## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## ⚠️ Common Issues

1. **DSPy Import Errors**
   ```bash
   # Install DSPy framework
   pip install dspy-ai>=3.0.3
   ```

2. **API Key Issues**
   ```bash
   # Verify environment variables (macOS/Linux)
   echo $OPENAI_API_KEY
   
   # Set environment variable if missing
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Model Configuration Errors**
   - Ensure you're using `gpt-4o-mini` instead of `gpt-5` 
   - GPT-5 requires specific parameters: `temperature=1.0` and `max_tokens >= 16000`

4. **File Not Found Errors**
   - Run agents from the project root directory
   - Ensure sample data files exist in their respective directories

5. **Dependencies Missing**
   ```bash
   # Reinstall all dependencies
   pip install -r requirements.txt
   ```

## 📝 License

MIT License - feel free to use and modify for your needs.

## 🙋‍♂️ Support

For issues and questions:
1. Check the [Issues](https://github.com/superagenticai/agentic-devops/issues) section
2. Create a new issue with detailed information