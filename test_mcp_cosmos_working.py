#!/usr/bin/env python3

import asyncio
import httpx
import json
from datetime import datetime, timezone


async def test_mcp_cosmos_working():
    """Test MCP server with working Cosmos DB insertion"""
    print("🧪 Testing MCP Server → Cosmos DB (Working Version)")
    print("=" * 60)
    
    mcp_url = "http://127.0.0.1:8080/mcp"
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            
            # Step 1: Get session ID
            print("🔍 Step 1: Getting session ID...")
            headers = {
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json"
            }
            
            init_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                },
                headers=headers
            )
            
            session_id = init_response.headers.get('mcp-session-id')
            if not session_id:
                print("❌ No session ID received")
                return False
                
            print(f"✅ Got session ID: {session_id}")
            
            # Set up headers with session for all subsequent requests
            headers_with_session = {
                "Accept": "application/json, text/event-stream", 
                "Content-Type": "application/json",
                "mcp-session-id": session_id
            }
            
            # Step 2: Initialize MCP session properly
            print("\n🔍 Step 2: Initializing MCP session...")
            init_request = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "clientInfo": {
                            "name": "TestClient",
                            "version": "1.0.0"
                        }
                    }
                },
                headers=headers_with_session
            )
            
            print(f"Init response status: {init_request.status_code}")
            if init_request.status_code != 200:
                print(f"❌ Initialization failed: {init_request.text}")
                return False
            
            # Step 3: List tools after initialization  
            print("\n🔍 Step 3: Listing available tools...")
            tools_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/list",
                    "params": {}
                },
                headers=headers_with_session
            )
            
            if tools_response.status_code == 200:
                response_text = tools_response.text
                if "event: message" in response_text and "data: " in response_text:
                    lines = response_text.split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data_json = line[6:]
                            result = json.loads(data_json)
                            
                            if "result" in result and "tools" in result["result"]:
                                tools = result["result"]["tools"]
                                print(f"✅ Available tools: {[tool['name'] for tool in tools]}")
                                
                                # Find Cosmos DB tool
                                cosmos_tool = None
                                for tool in tools:
                                    if "cosmos" in tool['name'].lower() or "insert" in tool['name'].lower():
                                        cosmos_tool = tool
                                        break
                                
                                if cosmos_tool:
                                    print(f"✅ Found Cosmos tool: {cosmos_tool['name']}")
                                    
                                    # Step 3: Insert test data
                                    print(f"\n🔍 Step 3: Inserting test data using {cosmos_tool['name']}...")
                                    
                                    test_document = {
                                        "id": f"mcp_test_{datetime.now(timezone.utc).isoformat().replace(':', '_')}",
                                        "timestamp": datetime.now(timezone.utc).isoformat(),
                                        "test_type": "mcp_working_test",
                                        "agent_name": "MCPTestAgent",
                                        "event_type": "successful_insertion",
                                        "data": {
                                            "message": "✅ MCP → Cosmos DB is working!",
                                            "session_id": session_id,
                                            "success": True
                                        },
                                        "partition_key": "mcp_test"
                                    }
                                    
                                    insert_response = await client.post(
                                        mcp_url,
                                        json={
                                            "jsonrpc": "2.0",
                                            "id": 4,
                                            "method": "tools/call",
                                            "params": {
                                                "name": cosmos_tool['name'],
                                                "arguments": {
                                                    "document": test_document,
                                                    "database": "playwright_logs",
                                                    "container": "actions"
                                                }
                                            }
                                        },
                                        headers=headers_with_session
                                    )
                                    
                                    if insert_response.status_code == 200:
                                        response_text = insert_response.text
                                        print(f"Insert response: {response_text[:300]}...")
                                        
                                        if "event: message" in response_text:
                                            lines = response_text.split('\n')
                                            for line in lines:
                                                if line.startswith('data: '):
                                                    data_json = line[6:]
                                                    insert_result = json.loads(data_json)
                                                    
                                                    if "result" in insert_result:
                                                        print("🎉 SUCCESS! Data inserted into Cosmos DB!")
                                                        print(f"📄 Document ID: {test_document['id']}")
                                                        print(f"📋 Result: {insert_result['result']}")
                                                        return True
                                                    elif "error" in insert_result:
                                                        print(f"❌ Insert error: {insert_result['error']}")
                                                        return False
                                    else:
                                        print(f"❌ Insert failed with status: {insert_response.status_code}")
                                        return False
                                else:
                                    print("❌ No Cosmos DB tool found")
                                    return False
                            elif "error" in result:
                                print(f"❌ Tools list error: {result['error']}")
                                return False
                            
            return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    print("🚀 Testing Complete MCP → Cosmos DB Flow\n")
    
    success = await test_mcp_cosmos_working()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! MCP → Cosmos DB is working!")
        print("✅ Check your Cosmos DB 'actions' container for the test document.")
        print("🔗 Database: playwright_logs, Container: actions")
    else:
        print("❌ MCP → Cosmos DB test failed.")


if __name__ == "__main__":
    asyncio.run(main())
