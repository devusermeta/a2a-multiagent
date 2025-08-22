#!/usr/bin/env python3

import asyncio
import httpx
import json


async def test_mcp_tools():
    """Test to get available tools from MCP server"""
    print("🧪 Testing MCP Server Tools")
    print("=" * 50)
    
    mcp_url = "http://127.0.0.1:8080/mcp"
    session_id = None
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            
            # Step 1: Initialize
            print("🔍 Step 1: Initialize...")
            response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "ToolsTestClient",
                            "version": "1.0.0"
                        }
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            session_id = response.headers.get('mcp-session-id')
            print(f"✅ Session ID: {session_id}")
            
            # Step 2: List tools
            print("\n🔍 Step 2: List tools...")
            tools_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": session_id
                }
            )
            
            print(f"Tools Response Status: {tools_response.status_code}")
            print(f"Tools Response: {tools_response.text}")
            
            # Parse event stream
            if "event: message" in tools_response.text:
                lines = tools_response.text.split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        data_json = line[6:]
                        result = json.loads(data_json)
                        if "result" in result and "tools" in result["result"]:
                            tools = result["result"]["tools"]
                            print(f"\n✅ Available tools:")
                            for tool in tools:
                                print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
                        elif "error" in result:
                            print(f"❌ Error: {result['error']}")
                            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
