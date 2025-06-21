# n8n + Claude Code Integration

## Environment Setup
- Use Python 3.9+ for n8n integration tools
- Store credentials in environment variables, never hardcode in source
- Required environment variables:
  ```bash
  export N8N_HOST_URL="https://gmgm.zeabur.app"
  export N8N_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkOWRhNjcyNS1kMTJjLTQzYzItOGJkOC04Y2Y5NjNjYzA4NmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzUwNDg4MjI2fQ.P-b1xY34XA4EjC2NMNMdquYc_gKXJYGRGsBtNkQy3Oo"
  ```
- Test connection: `curl -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_HOST_URL/api/v1/workflows"`

## Basic CLI Commands (n8n_integration.py)
- List all workflows: `python3 n8n_integration.py list-workflows`
- Get workflow details: `python3 n8n_integration.py get-workflow <WORKFLOW_ID>`
- Execute workflow: `python3 n8n_integration.py execute <WORKFLOW_ID>`
- Create sample workflow: `python3 n8n_integration.py create-sample`

## Advanced CLI Commands (claude_n8n_cli.py)
- Test API connectivity: `python3 claude_n8n_cli.py test`
- List active workflows only: `python3 claude_n8n_cli.py list --active`
- Activate workflow: `python3 claude_n8n_cli.py activate <WORKFLOW_ID>`
- Disable workflow: `python3 claude_n8n_cli.py activate <WORKFLOW_ID> --disable`
- Get execution history: `python3 claude_n8n_cli.py executions --workflow-id <ID> --limit 10`
- Generate webhook test URL: `python3 claude_n8n_cli.py webhook <WORKFLOW_ID>`
- Update workflow name: `python3 claude_n8n_cli.py update <ID> --name "New Name"`

## Direct API Commands
- List workflows: `curl -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_HOST_URL/api/v1/workflows"`
- Get workflow: `curl -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_HOST_URL/api/v1/workflows/{id}"`
- Execute workflow: `curl -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" -H "Content-Type: application/json" "$N8N_HOST_URL/api/v1/workflows/{id}/execute"`
- Get executions: `curl -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_HOST_URL/api/v1/executions"`

## MCP Server Integration
- Add to `~/.claude/claude_desktop_config.json`:
  ```json
  {
    "mcpServers": {
      "n8n-integration": {
        "command": "npx",
        "args": ["-y", "@ahmad.soliman/mcp-n8n-server"],
        "env": {
          "N8N_HOST_URL": "https://gmgm.zeabur.app",
          "N8N_API_KEY": "pcsk_7SezVC_fLKkAEMtjjdAf6EkFMXRvMbGg8BfeJ7v8CVDqmvdSuWRwke5ETmEDDd2M3Q2cY"
        }
      }
    }
  }
  ```
- Restart Claude Desktop to apply changes

## Common Workflow Patterns
- **Daily Data Fetch & Notify**: Cron trigger → API fetch → data processing → AI summary → email formatting → Gmail send
- **AI-Enhanced Processing**: Use Gemini/Claude nodes for intelligent content generation and analysis
- **Error Handling**: Always include error trigger nodes and notification workflows

## Claude + n8n Analysis Workflows
- Get workflow and analyze: `curl -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_HOST_URL/api/v1/workflows/{id}" | claude -p "Analyze this n8n workflow structure and suggest optimizations"`
- Monitor executions: `curl -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_HOST_URL/api/v1/executions?limit=5" | claude -p "Analyze these execution results for issues"`
- Design workflows: `claude -p "Design an n8n workflow for GitHub webhook → PR analysis → Slack notification"`

## Troubleshooting
- **API connection fails**: 
  - Check network: `curl -I $N8N_HOST_URL`
  - Verify API key: `python3 claude_n8n_cli.py test`
- **Workflow execution errors**:
  - Check execution logs: `python3 claude_n8n_cli.py executions --workflow-id <ID> --limit 5`
  - Get workflow status: `python3 claude_n8n_cli.py get <WORKFLOW_ID>`
- **Permission issues**: Ensure API key has full "workflows" scope in n8n settings

## Best Practices
- Prototype workflows in n8n UI first, then automate via CLI
- Version control important workflow JSON files in git
- Use Claude for workflow analysis: "Analyze workflow performance and suggest improvements"
- Set up failure notifications via n8n error workflows
- Always test workflows before production deployment
- Use descriptive workflow names and include documentation nodes

## Key API Endpoints Reference
| Function | Method | Endpoint |
|----------|--------|----------|
| List workflows | GET | `/api/v1/workflows` |
| Get workflow | GET | `/api/v1/workflows/{id}` |
| Execute workflow | POST | `/api/v1/workflows/{id}/execute` |
| Get executions | GET | `/api/v1/executions` |
| Create workflow | POST | `/api/v1/workflows` |
| Update workflow | PUT | `/api/v1/workflows/{id}` |
| Delete workflow | DELETE | `/api/v1/workflows/{id}` |