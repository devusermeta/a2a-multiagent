#!/usr/bin/env python3

import asyncio
import httpx
import json


async def test_direct_tool_call():
    """Test calling a tool directly"""
    print("🧪 Testing Direct Tool Call")
    print("=" * 50)
    
    mcp_url = "http://127.0.0.1:8080/mcp"
    
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
                            "name": "DirectToolTestClient",
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
            
            # Step 2: Try calling a known tool directly
            print(f"\n🔍 Step 2: Try calling list_collections tool...")
            
            tool_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "list_collections",
                        "arguments": {}
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": session_id
                }
            )
            
            print(f"Status: {tool_response.status_code}")
            print(f"Response: {tool_response.text}")
            
            if tool_response.status_code == 200:
                if "event: message" in tool_response.text:
                    lines = tool_response.text.split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data_json = line[6:]
                            result = json.loads(data_json)
                            if "result" in result:
                                print(f"✅ Tool result: {result['result']}")
                                return result['result']
                            elif "error" in result:
                                print(f"❌ Tool error: {result['error']}")
                            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_direct_tool_call())
