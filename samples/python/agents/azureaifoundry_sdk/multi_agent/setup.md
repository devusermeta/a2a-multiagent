# Azure AI Foundry Multi-Agent Setup Guide

## Prerequisites
- Python 3.13+
- Node.js and npm
- Azure AI Foundry Project with deployed language model
- uv package manager

## Quick Setup Commands

### 1. Navigate to Project
```powershell
cd "a2a-samples\samples\python\agents\azureaifoundry_sdk\multi_agent"
```

### 2. Setup Host Agent
```powershell
cd host_agent
uv sync
copy .env.example .env
```

### 3. Configure Azure Credentials
Edit `host_agent\.env`:
```env
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME = "your-gpt-4-deployment-name"
AZURE_AI_AGENT_ENDPOINT = "https://your-project.eastus2.inference.ai.azure.com/"
AZURE_AI_AGENT_SUBSCRIPTION_ID = "your-azure-subscription-id"
AZURE_AI_AGENT_RESOURCE_GROUP_NAME = "your-resource-group-name"
AZURE_AI_AGENT_PROJECT_NAME = "your-project-name"

PLAYWRIGHT_AGENT_URL=http://localhost:10001
TOOL_AGENT_URL=http://localhost:10002

LOG_LEVEL=INFO
DEBUG_MODE=false
```

### 4. Setup Tool Agent
```powershell
cd ..\remote_agents\tool_agent
uv sync
```

### 5. Setup Playwright Agent
```powershell
cd ..\playwright_agent
uv sync
uv add playwright
uv run playwright install
```

## Running the System

### Start Agents (3 Separate Terminals)

**Terminal 1 - Tool Agent:**
```powershell
cd "samples\python\agents\azureaifoundry_sdk\multi_agent\remote_agents\tool_agent";.venv\Scripts\activate ;python .
```

**Terminal 2 - Playwright Agent:**
```powershell
cd "samples\python\agents\azureaifoundry_sdk\multi_agent\remote_agents\playwright_agent";.venv\Scripts\activate;python .
```

**Terminal 3 - Host Agent:**
```powershell
cd "samples\python\agents\azureaifoundry_sdk\multi_agent\host_agent";.venv\Scripts\activate;python .
```

### Access Application
- Open browser: **http://localhost:8083**

## Testing Commands

### Test Tool Agent (Math/Logic)
```
Calculate the fibonacci sequence for the first 10 numbers
```

### Test Agent Discovery
```
What tools do you have available?
```

### Test Playwright Agent (Web Automation)
```
Navigate to github.com and describe what you see
```

## Expected Endpoints
- Tool Agent: http://localhost:10002
- Playwright Agent: http://localhost:10001
- Host Agent UI: http://localhost:8083

## Troubleshooting Commands

### Kill Process if Port Busy
```powershell
taskkill /F /PID <process_id>
```

### Check Node.js Installation
```powershell
node --version
npx --version
```

### Test Playwright MCP
```powershell
npx @playwright/mcp@latest --help
```

### Check Agent Status
Look for these log messages:
- Tool Agent: `INFO: Uvicorn running on http://localhost:10002`
- Playwright Agent: `INFO: Uvicorn running on http://localhost:10001`
- Host Agent: `* Running on local URL: http://0.0.0.0:8083`

## Known Issues
- Playwright Agent may have task retrieval errors (initialization issues)
- Tool Agent should work fine for math/calculation tasks
- Ensure all Azure credentials are correctly configured

## Directory Structure After Setup
```
multi_agent/
├── host_agent/
│   ├── .venv/
│   ├── .env
│   └── ...
├── remote_agents/
│   ├── tool_agent/
│   │   ├── .venv/
│   │   └── ...
│   └── playwright_agent/
│       ├── .venv/
│       └── ...
```
