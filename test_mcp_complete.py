#!/usr/bin/env python3

import asyncio
import httpx
import json


async def test_mcp_complete():
    """Test complete MCP workflow"""
    print("🧪 Testing Complete MCP Workflow")
    print("=" * 50)
    
    mcp_url = "http://127.0.0.1:8080/mcp"
    session_id = None
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            
            # Step 1: Initialize and get session
            print("🔍 Step 1: Initialize and get session...")
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
                            "name": "CompleteTestClient",
                            "version": "1.0.0"
                        }
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            # Extract session ID from both possible header names
            session_id = response.headers.get('mcp-session-id') or response.headers.get('x-session-id')
            print(f"✅ Session ID: {session_id}")
            print(f"✅ Response status: {response.status_code}")
            
            if not session_id:
                print("❌ No session ID found")
                return
                
            # Step 2: Try tools/list with the session ID 
            print(f"\n🔍 Step 2: List tools with session {session_id}...")
            
            # Try both header formats
            for header_name in ['mcp-session-id', 'x-session-id']:
                print(f"  Trying with {header_name}...")
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
                        header_name: session_id
                    }
                )
                
                print(f"  Status: {tools_response.status_code}")
                print(f"  Response: {tools_response.text[:200]}...")
                
                if tools_response.status_code == 200 and "error" not in tools_response.text:
                    print(f"  ✅ Success with {header_name}!")
                    
                    # Parse response 
                    if "event: message" in tools_response.text:
                        lines = tools_response.text.split('\n')
                        for line in lines:
                            if line.startswith('data: '):
                                data_json = line[6:]
                                result = json.loads(data_json)
                                if "result" in result and "tools" in result["result"]:
                                    tools = result["result"]["tools"]
                                    print(f"  ✅ Available tools:")
                                    for tool in tools:
                                        print(f"    - {tool['name']}: {tool.get('description', 'No description')}")
                                    return tools
                    break
                else:
                    print(f"  ❌ Failed with {header_name}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_complete())
