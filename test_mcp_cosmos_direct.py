#!/usr/bin/env python3

import asyncio
import httpx
import json
from datetime import datetime, timezone


async def test_mcp_cosmos_direct():
    """Test direct MCP server Cosmos DB functionality"""
    print("🧪 Testing MCP Server → Cosmos DB Direct Connection")
    print("=" * 60)
    
    mcp_url = "http://127.0.0.1:8080/mcp"
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            
            # Test 1: List available tools
            print("🔍 Step 1: Listing available MCP tools...")
            tools_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            if tools_response.status_code == 200:
                tools_result = tools_response.json()
                print(f"✅ MCP Tools List Response: {tools_result}")
                
                if "result" in tools_result and "tools" in tools_result["result"]:
                    tools = tools_result["result"]["tools"]
                    print(f"📋 Available tools: {[tool['name'] for tool in tools]}")
                    
                    # Find Cosmos DB tool
                    cosmos_tools = [t for t in tools if "cosmos" in t.get("name", "").lower()]
                    if cosmos_tools:
                        print(f"✅ Found Cosmos DB tools: {[t['name'] for t in cosmos_tools]}")
                        cosmos_tool_name = cosmos_tools[0]['name']
                    else:
                        print("❌ No Cosmos DB tools found!")
                        return False
                else:
                    print("❌ Unexpected tools/list response format")
                    return False
            else:
                print(f"❌ Failed to list tools: HTTP {tools_response.status_code}")
                print(f"Response: {tools_response.text}")
                return False
            
            # Test 2: Insert test data into Cosmos DB
            #!/usr/bin/env python3

import asyncio
import httpx
import json
from datetime import datetime, timezone


async def test_mcp_cosmos_direct():
    """Test direct MCP server Cosmos DB functionality with proper session management"""
    print("🧪 Testing MCP Server → Cosmos DB Direct Connection")
    print("=" * 60)
    
    mcp_url = "http://127.0.0.1:8080/mcp"
    session_id = None
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            
            # Step 1: Initialize MCP session
            print("🔍 Step 1: Initializing MCP session...")
            init_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 0,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "clientInfo": {
                            "name": "DirectTestClient",
                            "version": "1.0.0"
                        }
                    }
                },
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json"
                }
            )
            
            if init_response.status_code == 200:
                init_result = init_response.json()
                session_id = init_response.headers.get('x-session-id')
                print(f"✅ MCP session initialized. Session ID: {session_id}")
                print(f"📋 Server capabilities: {init_result.get('result', {}).get('capabilities', {})}")
            else:
                print(f"❌ Failed to initialize session: HTTP {init_response.status_code}")
                print(f"Response: {init_response.text}")
                return False
            
            if not session_id:
                print("❌ No session ID received from server")
                return False
            
            # Step 2: List available tools using session ID
            print(f"
🔍 Step 2: Listing available MCP tools with session {session_id}...")
            tools_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                },
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json",
                    "x-session-id": session_id
                }
            )
            
            if tools_response.status_code == 200:
                tools_result = tools_response.json()
                print(f"✅ MCP Tools List Response: {tools_result}")
                
                if "result" in tools_result and "tools" in tools_result["result"]:
                    tools = tools_result["result"]["tools"]
                    print(f"📋 Available tools: {[tool['name'] for tool in tools]}")
                    
                    # Find Cosmos DB tool
                    cosmos_tools = [t for t in tools if "cosmos" in t.get("name", "").lower()]
                    if cosmos_tools:
                        print(f"✅ Found Cosmos DB tools: {[t['name'] for t in cosmos_tools]}")
                        cosmos_tool_name = cosmos_tools[0]['name']
                    else:
                        print("❌ No Cosmos DB tools found!")
                        return False
                else:
                    print("❌ Unexpected tools/list response format")
                    return False
            else:
                print(f"❌ Failed to list tools: HTTP {tools_response.status_code}")
                print(f"Response: {tools_response.text}")
                return False
            
            # Step 3: Insert test data into Cosmos DB
            print(f"
🔍 Step 3: Testing {cosmos_tool_name} insertion...")
            
            test_document = {
                "id": f"mcp_test_{datetime.now(timezone.utc).isoformat()}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "test_type": "direct_mcp_test",
                "agent_name": "MCPTestAgent",
                "event_type": "test_insertion",
                "data": {
                    "message": "Testing direct MCP → Cosmos DB connection",
                    "success": True
                },
                "partition_key": "mcp_test"
            }
            
            insert_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": cosmos_tool_name,
                        "arguments": {
                            "document": test_document,
                            "database": "playwright_logs",
                            "container": "actions"
                        }
                    }
                },
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json",
                    "x-session-id": session_id
                }
            )
            
            if insert_response.status_code == 200:
                insert_result = insert_response.json()
                print(f"✅ Cosmos DB Insert Response: {insert_result}")
                
                if "result" in insert_result:
                    print("🎉 SUCCESS! Data inserted into Cosmos DB!")
                    print(f"📄 Document ID: {test_document['id']}")
                    return True
                else:
                    print(f"❌ Insert failed: {insert_result}")
                    return False
            else:
                print(f"❌ Failed to insert into Cosmos DB: HTTP {insert_response.status_code}")
                print(f"Response: {insert_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing MCP → Cosmos DB: {e}")
        return False


async def main():
    success = await test_mcp_cosmos_direct()
    
    print("
" + "=" * 60)
    if success:
        print("🎉 MCP → Cosmos DB connection is working!")
        print("✅ You should now see the test document in your Cosmos DB container.")
        print("🔗 Check the 'actions' container in the 'playwright_logs' database.")
    else:
        print("❌ MCP → Cosmos DB connection failed.")
        print("🔧 Check MCP server logs and Cosmos DB configuration.")


if __name__ == "__main__":
    asyncio.run(main())
            
            test_document = {
                "id": f"mcp_test_{datetime.now(timezone.utc).isoformat()}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "test_type": "direct_mcp_test",
                "agent_name": "MCPTestAgent",
                "event_type": "test_insertion",
                "data": {
                    "message": "Testing direct MCP → Cosmos DB connection",
                    "success": True
                },
                "partition_key": "mcp_test"
            }
            
            insert_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": cosmos_tool_name,
                        "arguments": {
                            "document": test_document,
                            "database": "playwright_logs",
                            "container": "actions"
                        }
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            if insert_response.status_code == 200:
                insert_result = insert_response.json()
                print(f"✅ Cosmos DB Insert Response: {insert_result}")
                
                if "result" in insert_result:
                    print("🎉 SUCCESS! Data inserted into Cosmos DB!")
                    print(f"📄 Document ID: {test_document['id']}")
                    return True
                else:
                    print(f"❌ Insert failed: {insert_result}")
                    return False
            else:
                print(f"❌ Failed to insert into Cosmos DB: HTTP {insert_response.status_code}")
                print(f"Response: {insert_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing MCP → Cosmos DB: {e}")
        return False


async def main():
    success = await test_mcp_cosmos_direct()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 MCP → Cosmos DB connection is working!")
        print("✅ You should now see the test document in your Cosmos DB container.")
        print("🔗 Check the 'actions' container in the 'playwright_logs' database.")
    else:
        print("❌ MCP → Cosmos DB connection failed.")
        print("🔧 Check MCP server logs and Cosmos DB configuration.")


if __name__ == "__main__":
    asyncio.run(main())
