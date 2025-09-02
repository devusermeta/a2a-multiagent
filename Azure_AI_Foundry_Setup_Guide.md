# Azure AI Foundry Multi-Agent Setup & Troubleshooting Guide

## Overview
This document provides a complete guide for setting up Azure AI Foundry with multi-agent systems, including troubleshooting steps for common connection issues encountered during resource recreation.

## Problem Summary
After accidentally deleting an Azure resource group, we needed to recreate Azure AI Foundry resources with identical names to maintain existing `.env` configurations. The main challenges were:
- Regional compatibility issues (Agents feature not available in all regions)
- Endpoint format changes between old and new Azure AI Foundry implementations
- Library migration from `azure.ai.agents` to `azure.ai.projects`

## Prerequisites
- Azure CLI installed and authenticated
- Azure ML CLI extension
- Python 3.13+
- Appropriate Azure permissions for resource creation

## Step-by-Step Solution

### 1. Install Required Azure CLI Extensions

```powershell
# Install Azure ML CLI extension v2
az extension add --name ml
```

### 2. Create Resource Group and Azure AI Foundry Infrastructure

```powershell
# Create resource group in eastus (important: use a region that supports Agents)
az group create --name Captain-Planaut --location eastus

# Create Azure ML workspace (Hub)
az ml workspace create --resource-group Captain-Planaut --name captainplanautagents-resource --kind hub --location eastus

# Create Azure ML workspace (Project)  
az ml workspace create --resource-group Captain-Planaut --name captainplanautagents --kind project --location eastus --hub-id /subscriptions/e0783b50-4ca5-4059-83c1-524f39faa624/resourceGroups/Captain-Planaut/providers/Microsoft.MachineLearningServices/workspaces/captainplanautagents-resource
```

### 3. Create Required Connections

#### Azure AI Search Connection
```powershell
# Create Azure AI Search service
az search service create --name agent-search268189676043 --resource-group Captain-Planaut --location eastus --sku standard

# Get the search service admin key
az search admin-key show --service-name agent-search268189676043 --resource-group Captain-Planaut
```

#### Use Existing OpenAI Resource (Cost-Effective Approach)
```powershell
# List existing OpenAI resources to find one in a supported region
az cognitiveservices account list --query "[?kind=='OpenAI'].{name:name, resourceGroup:resourceGroup, location:location, endpoint:properties.endpoint}" --output table

# Check deployments on existing resource
az cognitiveservices account deployment list --name macae-openai-7dfokqmjfelni --resource-group autogen-accelerator --query "[].{deploymentName:name, modelName:properties.model.name, modelVersion:properties.model.version, status:properties.provisioningState}" --output table
```

### 4. Create and Configure Capability Host

#### Create YAML Configuration File
```yaml
# capability_host.yaml
$schema: https://azuremlschemas.azureedge.net/latest/capabilityHost.schema.json
name: default
ai_services_connections:
  - macaeopenai7dfokqmjfelni
storage_connections:
  - captainplanautagents/workspaceblobstore
vector_store_connections:
  - agentsearch268189676043
```

#### Apply Capability Host Configuration
```powershell
# Delete existing capability host if needed
az ml capability-host delete --resource-group Captain-Planaut --workspace-name captainplanautagents --name default

# Create new capability host with correct connections
az ml capability-host create --resource-group Captain-Planaut --workspace-name captainplanautagents --file capability_host.yaml
```

### 5. Clean Up Stale Connections

```powershell
# List all connections
az ml connection list --resource-group Captain-Planaut --workspace-name captainplanautagents --output table

# Delete stale connections that point to deleted resources
az ml connection delete --resource-group Captain-Planaut --workspace-name captainplanautagents --name "Abhin-mf297s4l-northcentralus_aoai"
az ml connection delete --resource-group Captain-Planaut --workspace-name captainplanautagents --name "abhinmf297s4lnorthcentralus_aoai"
az ml connection delete --resource-group Captain-Planaut --workspace-name captainplanautagents --name "abhinmf297s4lnorthcentralus"
```

### 6. Get Correct Azure AI Foundry Endpoint

```powershell
# Get the workspace details to find the correct agents endpoint
az ml workspace show --resource-group Captain-Planaut --name captainplanautagents --query "agentsEndpointUri" --output tsv
```

Expected output format:
```
https://eastus.api.azureml.ms/agents/v1.0/subscriptions/e0783b50-4ca5-4059-83c1-524f39faa624/resourceGroups/Captain-Planaut/providers/Microsoft.MachineLearningServices/workspaces/captainplanautagents
```

## Code Changes Required

### 1. Update .env Files

Update all `.env` files in your agents with the correct endpoint:

```properties
# OLD (doesn't work)
AZURE_AI_AGENT_ENDPOINT = "https://captainplanautagents-resource.services.ai.azure.com/api/projects/captainplanautagents"

# NEW (working)
AZURE_AI_AGENT_ENDPOINT = "https://eastus.api.azureml.ms/agents/v1.0/subscriptions/e0783b50-4ca5-4059-83c1-524f39faa624/resourceGroups/Captain-Planaut/providers/Microsoft.MachineLearningServices/workspaces/captainplanautagents"
```

### 2. Update Python Code - Library Migration

#### From azure.ai.agents to azure.ai.projects

**OLD CODE:**
```python
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ListSortOrder

# Initialize Azure AI Agents client
self.agents_client = AgentsClient(
    endpoint=os.environ["AZURE_AI_AGENT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Later in code
messages = self.agents_client.messages.list(
    thread_id=self.current_thread.id, 
    order=ListSortOrder.DESCENDING
)
```

**NEW CODE:**
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Initialize Azure AI Project client (for Azure AI Foundry agents)
self.project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_AGENT_ENDPOINT"],
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_AI_AGENT_SUBSCRIPTION_ID"],
    resource_group_name=os.environ["AZURE_AI_AGENT_RESOURCE_GROUP_NAME"],
    project_name=os.environ["AZURE_AI_AGENT_PROJECT_NAME"]
)
# Use the project client's agents interface
self.agents_client = self.project_client.agents

# Later in code (note: string instead of enum)
messages = self.agents_client.messages.list(
    thread_id=self.current_thread.id, 
    order="desc"
)
```

### 3. Update Gradio Configuration

Fix localhost accessibility issues:

```python
# OLD
demo.queue().launch(
    server_name="0.0.0.0",
    server_port=8083,
)

# NEW
demo.queue().launch(
    server_name="127.0.0.1",
    server_port=8083,
    share=False,
    inbrowser=True
)
```

## Diagnostic and Testing

### Create Diagnostic Script

```python
# test_azure_ai_connection.py
#!/usr/bin/env python3
"""
Azure AI Foundry Connection Test Script
"""
import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        endpoint = os.getenv("AZURE_AI_AGENT_ENDPOINT")
        credential = DefaultAzureCredential()
        
        project_client = AIProjectClient(
            endpoint=endpoint,
            credential=credential
        )
        
        agents_client = project_client.agents
        agents = agents_client.list_agents()
        print(f"✅ Success: Found {len(list(agents))} agents")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_connection()
```

### Verification Commands

```powershell
# Verify capability host configuration
az ml capability-host show --resource-group Captain-Planaut --workspace-name captainplanautagents --name default

# Verify connections
az ml connection list --resource-group Captain-Planaut --workspace-name captainplanautagents --query "[].{name:name, target:target}" --output table

# Test Python connection
python test_azure_ai_connection.py
```

## Regional Compatibility

### Supported Regions for Azure AI Foundry Agents
- australiaeast
- brazilsouth  
- canadaeast
- centraluseuap
- **eastus** ✅ (recommended)
- eastus2
- francecentral
- germanywestcentral
- italynorth
- japaneast
- koreacentral
- norwayeast
- polandcentral
- southafricanorth
- southcentralus
- southeastasia
- swedencentral
- switzerlandnorth
- uaenorth
- uksouth
- westus
- westus3

### Unsupported Regions
- **northcentralus** ❌ (caused our original issue)
- Other regions not listed above

## Running the Multi-Agent System

### Start All Agents (in separate terminals)

```powershell
# Terminal 1 - Playwright Agent
cd "samples\python\agents\azureaifoundry_sdk\multi_agent\remote_agents\playwright_agent"
.venv\Scripts\activate
python .

# Terminal 2 - Tool Agent  
cd "samples\python\agents\azureaifoundry_sdk\multi_agent\remote_agents\tool_agent"
.venv\Scripts\activate 
python .

# Terminal 3 - Time Agent
cd "samples\python\agents\azureaifoundry_sdk\multi_agent\remote_agents\time_agent"
.venv\Scripts\activate
python .

# Terminal 4 - Cosmos Query Agent
cd "samples\python\agents\azureaifoundry_sdk\multi_agent\remote_agents\cosmos_query_agent"
.venv\Scripts\activate
python __main__.py --host localhost --port 10004

# Terminal 5 - Host Agent (main interface)
cd "samples\python\agents\azureaifoundry_sdk\multi_agent\host_agent"
.venv\Scripts\activate
python .
```

### Access Points
- **Main UI**: http://127.0.0.1:8083
- **Playwright Agent**: http://localhost:10001
- **Tool Agent**: http://localhost:10002  
- **Time Agent**: http://localhost:10003
- **Cosmos Query Agent**: http://localhost:10004

## Cost Optimization

### Resource Reuse Strategy
- ✅ **Reused existing OpenAI resource** in eastus region
- ✅ **Deleted unused resources** created during troubleshooting
- ✅ **Minimal new infrastructure** - only created what was necessary

### Cleanup Commands
```powershell
# Remove unused OpenAI resources
az cognitiveservices account delete --name captainplanaut-eastus-openai --resource-group Captain-Planaut
az cognitiveservices account delete --name abhin-mf297s4l-northcentralus --resource-group Captain-Planaut

# Clean up temporary files
del search_connection.yaml
del capability_host.yaml
del storage_connection.yaml
del test_azure_ai_connection.py
```

## Troubleshooting Common Issues

### Issue 1: "Subdomain does not map to a resource"
**Cause**: Wrong endpoint format or region incompatibility
**Solution**: Use the correct Azure ML agents endpoint format

### Issue 2: "Unsupported region" in Azure AI Studio
**Cause**: Azure OpenAI resource in unsupported region
**Solution**: Create/use OpenAI resource in supported region

### Issue 3: Agents not connecting to remote agents
**Cause**: Remote agents not running or using wrong endpoint
**Solution**: Ensure all agents have correct endpoint and are running

### Issue 4: Gradio localhost error
**Cause**: Network accessibility issues
**Solution**: Use 127.0.0.1 instead of 0.0.0.0

## Success Indicators

✅ Host agent creates Azure AI agents successfully  
✅ Message and thread creation works  
✅ Remote agents respond to discovery requests  
✅ Playwright agent can browse web and extract data  
✅ No "Subdomain does not map to a resource" errors  
✅ Gradio UI accessible at http://127.0.0.1:8083  

## Key Learnings

1. **Regional compatibility is critical** - Not all Azure regions support AI Foundry Agents
2. **Endpoint format matters** - Use the ML workspace agents endpoint, not the old service endpoint
3. **Library migration required** - New Azure AI Foundry uses `azure.ai.projects` instead of `azure.ai.agents`
4. **Resource reuse saves costs** - Always check for existing compatible resources before creating new ones
5. **Capability hosts need correct connections** - Ensure all connections point to valid, accessible resources

---

**Document Created**: September 2, 2025  
**Azure AI Foundry Version**: Latest (using azure.ai.projects library)  
**Status**: ✅ Fully Functional Multi-Agent System
