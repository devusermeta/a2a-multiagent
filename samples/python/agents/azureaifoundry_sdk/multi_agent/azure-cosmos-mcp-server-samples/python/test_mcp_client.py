#!/usr/bin/env python3
"""
Simple MCP client to test the Azure Cosmos DB MCP server
"""

import asyncio
import json
import aiohttp
from datetime import datetime

async def test_mcp_server():
    """Test the MCP server by making direct HTTP requests"""
    
    mcp_url = "http://localhost:8080/mcp"
    
    # Create an aiohttp session
    async with aiohttp.ClientSession() as session:
        
        # Test 1: List available tools
        print("🔧 Testing MCP server - listing available tools...")
        
        tools_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        try:
            async with session.post(
                mcp_url,
                json=tools_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Tools response: {json.dumps(result, indent=2)}")
                else:
                    text = await response.text()
                    print(f"❌ Error response ({response.status}): {text}")
                    
        except Exception as e:
            print(f"❌ Error calling MCP server: {e}")
            
        # Test 2: Try to query Cosmos DB data
        print(f"\n📊 Testing MCP server - querying Cosmos DB...")
        
        # Assuming there might be a query tool based on typical MCP patterns
        query_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "query_cosmos",  # This might not be the exact tool name
                "arguments": {
                    "query": "SELECT * FROM c WHERE c.agent_name = 'TimeAgent' ORDER BY c._ts DESC"
                }
            }
        }
        
        try:
            async with session.post(
                mcp_url,
                json=query_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Query response: {json.dumps(result, indent=2)}")
                else:
                    text = await response.text()
                    print(f"❌ Query error ({response.status}): {text}")
                    
        except Exception as e:
            print(f"❌ Error querying via MCP: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
