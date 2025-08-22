#!/usr/bin/env python3

import asyncio
import httpx
import json


async def proper_mcp_sequence():
    """Follow proper MCP initialization sequence"""
    print("🧪 Proper MCP Protocol Sequence")
    print("=" * 50)
    
    mcp_url = "http://127.0.0.1:8080/mcp"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            
            # Step 1: Initialize MCP session
            print("🔍 Step 1: Initialize MCP session...")
            init_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "clientInfo": {
                            "name": "ProperMCPClient",
                            "version": "1.0.0"
                        }
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            session_id = init_response.headers.get('mcp-session-id')
            print(f"  Session ID: {session_id}")
            print(f"  Init Status: {init_response.status_code}")
            
            # Parse initialization response
            if "event: message" in init_response.text:
                lines = init_response.text.split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        data_json = line[6:]
                        init_result = json.loads(data_json)
                        print(f"  Init Result: {init_result}")
                        
                        if "result" in init_result:
                            server_capabilities = init_result["result"].get("capabilities", {})
                            print(f"  Server Capabilities: {server_capabilities}")
            
            # Step 2: Send initialized notification
            print("\n🔍 Step 2: Send initialized notification...")
            notification_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {}
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": session_id
                }
            )
            
            print(f"  Notification Status: {notification_response.status_code}")
            print(f"  Notification Response: {notification_response.text[:200]}")
            
            # Step 3: Now try calling a tool
            print("\n🔍 Step 3: Try calling tool after proper initialization...")
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
            
            print(f"  Tool Status: {tool_response.status_code}")
            print(f"  Tool Response: {tool_response.text}")
            
            # Try to parse tool result
            if "event: message" in tool_response.text:
                lines = tool_response.text.split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        data_json = line[6:]
                        tool_result = json.loads(data_json)
                        if "result" in tool_result:
                            print(f"  ✅ Tool Success: {tool_result['result']}")
                        elif "error" in tool_result:
                            print(f"  ❌ Tool Error: {tool_result['error']}")
                            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(proper_mcp_sequence())
