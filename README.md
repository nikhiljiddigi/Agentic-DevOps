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
pip3 install -r requirements.txt
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

2. **Run the complete workflow:**
   ```bash
   # Pre-commit stage (PR review, config validation, security scanning)
   python3 run_agentic_flow.py --stage pr
   
   # Build stage (CI/CD failure analysis)
   python3 run_agentic_flow.py --stage build
   
   # Post-deploy stage (anomaly detection, incident response)
   python3 run_agentic_flow.py --stage post
   ```

4. **Or run individual agents:**
   ```bash
   python3 cicd_failure_explainer/agent.py
   ```

That's it! The agents work with mock data by default, so you can explore their capabilities immediately.

## 📋 Sample Output

### Stage 1: Pre-Commit (`--stage pr`)
```bash
$ python3 run_agentic_flow.py --stage pr

🚀 Starting MCP server in background: npx -y @modelcontextprotocol/server-github
✅ MCP server started successfully
🔗 Connected to MCP server with 4 tools
✅ Real MCP Connected! Available tools: ['search_repositories', 'get_file_contents', 'list_issues', 'get_repository']
📡 Real MCP Request - Context: Get PR details for https://github.com/Tejaswan/spr...

📋 PR Review Results:

Security Issues:
  - No security issues identified in the current codebase

Edge Cases:
  - No potential edge cases detected

Doc Updates:
  - No documentation updates required

Doc Suggestions:
  - Documentation appears to be complete

Impact Analysis:
  The changes in the specified commit involve updates to the Spring Boot application, which may include modifications to the business logic, configuration files, or dependencies. Analyzing the impact, these changes could affect the application's functionality, performance, or security. It is crucial to review the specific files altered to determine if any critical components are involved, such as controllers, services, or repositories. Testing should be conducted to ensure that the application behaves as expected after the changes.

Risk Score:
  0.7

----------------------------------------

✅ Pre-Deploy Validation Results:
Warnings:
  - The image 'myregistry/auth-service:latest' is using the 'latest' tag, which can lead to unpredictable deployments.
  - No readiness probe is defined, which may affect the service's availability during startup.

🔥 Root Warning: "The use of the 'latest' tag for the image can lead to unpredictable behavior in production environments."

⚖️  Risk Score: 7.50

🩺 Recommendations:
  - Specify a fixed version tag for the container image instead of using 'latest'.
  - Add a readiness probe to ensure the service is fully initialized before receiving traffic.

----------------------------------------

✅ Security Scan Results:

🔐 Hardcoded Secrets Detected:
  - Line 3: Bearer token
  - Line 4: Hardcoded password

🧠 Summary: Detected security issues in code or dependencies.
   - Known vulnerable dependency versions found.
   - Hardcoded credentials present in source.
🩺 Fix:
   - Upgrade vulnerable packages (e.g., requests ≥ 2.20.0).
   - Remove hardcoded tokens; use environment variables.
```

### Stage 2: Build (`--stage build`)
```bash
$ python3 run_agentic_flow.py --stage build

🔍 Running CI/CD Failure Analysis for: demo-pipeline-001
Root Cause: The root cause of the pipeline failure is a database connection timeout, indicating that the database server (db-prod.company.com:5432) is unreachable due to network issues or server unavailability.
Fix Suggestions:
  - Check the database server status to ensure it is running and accessible.
  - Verify network configurations and firewall settings to allow connections to the database server.
  - Increase the timeout settings for database connections if necessary.
  - Consult with the infrastructure team to investigate any ongoing network issues.
  - Ensure that the database connection string and credentials are correct.
Impact Level: High
```

### Stage 3: Post-Deploy (`--stage post`)
```bash
$ python3 run_agentic_flow.py --stage post 

✅ Anomaly Report:
  - CPU usage 93% exceeds 85%
  - Memory usage 89% exceeds 85%
  - High latency 320 ms
  - 5 pod restarts detected

🧠 Status: Unhealthy
📖 Explanation: Possible high workload or tight loop. | Memory leak or unbounded cache growth. | Network congestion or backend slowdown. | CrashLoop or readiness probe failures.

🩺 Recommendations:
  - Check top CPU pods; consider HPA scaling.
  - Review memory limits; restart leaking pods.
  - Check downstream service response times.
  - Inspect pod logs and readiness config.

✅ Infra RCA Summary Report:

🔥 Root Cause: The root cause of the incident was a misconfiguration in the database connection pool settings, which led to timeouts and high CPU usage in the payments service, resulting in a series of cascading failures including checkout API errors.

🧩 Affected Components:
  - payments-service
  - order-db
  - checkout API
  - payments-node

💥 Impact Summary: The payments service experienced a 42-minute outage characterized by high CPU usage, database timeouts, and multiple 503 errors from the checkout API, affecting transaction processing and user experience.

🩺 Resolution Steps:
  - Rollback to previous deployment succeeded
  - Adjusted database connection pool settings
  - Monitored system performance post-resolution
```

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
python3 cicd_failure_explainer/agent.py
```
Analyzes CI/CD pipeline failures and provides:
- Root cause analysis
- Remediation suggestions
- Impact assessment

### Incident RCA Generator
```bash
python3 incident_rca_generator/agent.py
```
Generates comprehensive incident analysis including:
- Root cause identification
- Timeline reconstruction
- Preventive measures

### Infrastructure Anomaly Explainer
```bash
python3 infra_anamoly_explainer/agent.py
```
Detects and explains infrastructure issues:
- Performance anomalies
- Resource utilization patterns
- System health insights

### PR Reviewer
```bash
python3 pr_reviewer/agent.py
```
Automated code review providing:
- Security vulnerability detection
- Code quality analysis
- Best practices recommendations

### Pre-Deploy Config Gate
```bash
python3 predeploy_config_gate/agent.py
```
Validates deployment configurations:
- Configuration syntax checking
- Security policy compliance
- Resource allocation validation

### Security Vulnerability Watcher
```bash
python3 security_vulnerability_watcher/agent.py
```
Monitors security vulnerabilities:
- Code vulnerability scanning
- Dependency analysis
- Security recommendations



## 📁 Project Structure

```
agentic-devops/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies  
├── run_agentic_flow.py                # Master orchestrator script
├── cicd_failure_explainer/            # CI/CD pipeline failure analysis
│   ├── agent.py
│   └── pipeline.log
├── incident_rca_generator/             # Incident root cause analysis
│   ├── agent.py
│   └── alerts.json
├── infra_anamoly_explainer/           # Infrastructure anomaly detection
│   ├── agent.py
│   └── metrics.json
├── pr_reviewer/                        # Automated code review
│   └── agent.py
├── predeploy_config_gate/             # Deployment configuration validation
│   ├── agent.py
│   └── deploy.yaml
├── security_vulnerability_watcher/     # Security vulnerability monitoring
│   ├── agent.py
│   ├── requirements.txt
│   └── requests.py
└── shared/                            # Shared utilities
    ├── config.py                      # DSPy configuration
    └── mcp_client.py                  # Mock MCP client
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