# Agentic DevOps

The concept of Agentic DevOps got introduced in Microsoft Build conference 2025. Agentic DevOps is a paradigm, not a product. It's accessible to all, regardless of your tech stack or tooling. Use AI-powered tools like Cursor, Windsurf, Claude Code, Continue, Cline, or open-source models like Llama 4, Mistral, DeepSeek, Qwen. Deploy on-prem with vLLM, SGLang, or in the cloud with AWS, GCP, Azure.

# Agentic DevOps with DSPy + MCP

A comprehensive demonstration of Agentic DevOps using DSPy and Model Context Protocol (MCP). The convep

This suite includes three specialized agents and a combined demo showcasing automated PR reviews, tech debt analysis, and incident response.

## 🎯 Features

- **PR Review Agent**: Automated security analysis, documentation review, and impact assessment
- **Tech Debt Agent**: Dependency analysis, code complexity scanning, and test coverage reporting
- **Incident Response Agent**: Automated incident diagnosis, remediation, and reporting

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
pip install "agenspy[mcp]" dspy openai
```

4. Install Node.js dependencies:
```bash
npm install -g @modelcontextprotocol/server-github
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

## 🖥️ Running Individual Demos

### PR Review Agent
```bash
python pr_review_agent.py
```
This will analyze a sample PR and provide:
- Security analysis
- Documentation review
- Implementation suggestions
- Impact assessment

### Tech Debt Agent
```bash
python tech_debt_agent.py
```
This will scan a repository for:
- Deprecated dependencies
- Complex code modules
- Test coverage gaps
- Refactoring opportunities

### Incident Response Agent
```bash
python incident_response_agent.py
```
This will simulate incident handling with:
- Automated diagnostics
- Remediation attempts
- Incident reporting
- On-call notifications

## 🎮 Running the Complete Demo

```bash
python agentic_devops_demo.py
```

This will run all three agents in sequence, demonstrating:
1. PR review workflow
2. Technical debt analysis
3. Incident response simulation

## 📁 Project Structure

```
agentic-devops/
├── pr_review_agent.py      # PR review automation
├── tech_debt_agent.py      # Technical debt analysis
├── incident_response_agent.py  # Incident response automation
└── README.md
```

## 🔑 API Keys and Permissions

### OpenAI API Key
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Copy and set as `OPENAI_API_KEY`

### GitHub Token
1. Visit [GitHub Settings > Developer Settings](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Select scopes:
   - `repo` (full access)
   - `read:org`
   - `workflow`
4. Copy and set as `GITHUB_TOKEN`


## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## ⚠️ Common Issues

1. **MCP Server Connection Failed**
   ```bash
   # Check if server is running
   ps aux | grep mcp
   # Restart server
   npx @modelcontextprotocol/server-github
   ```

2. **API Key Issues**
   ```bash
   # Verify environment variables
   echo $OPENAI_API_KEY
   echo $GITHUB_TOKEN
   ```

3. **Dependencies Missing**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   npm install -g @modelcontextprotocol/server-github
   ```

## 📝 License

MIT License - feel free to use and modify for your needs.

## 🙋‍♂️ Support

For issues and questions:
1. Check the [Issues](https://github.com/superagenticai/agentic-devops/issues) section
2. Create a new issue with detailed information