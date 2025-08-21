#!/usr/bin/env python3

import asyncio
import httpx
import json
from datetime import datetime, timezone


async def test_direct_cosmos_insert():
    """Test direct Cosmos DB insertion without tools/list"""
    print("🧪 Testing Direct Cosmos DB Insertion")
    print("=" * 50)
    
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
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "clientInfo": {"name": "TestClient", "version": "1.0.0"}
                    }
                },
                headers=headers
            )
            
            session_id = init_response.headers.get('mcp-session-id')
            if not session_id:
                print("❌ No session ID received")
                return False
                
            print(f"✅ Got session ID: {session_id}")
            
            headers_with_session = {
                "Accept": "application/json, text/event-stream", 
                "Content-Type": "application/json",
                "mcp-session-id": session_id
            }
            
            # Step 2: Try direct Cosmos DB insertion
            print("\n🔍 Step 2: Attempting direct Cosmos DB insertion...")
            
            test_document = {
                "id": f"direct_test_{datetime.now(timezone.utc).isoformat().replace(':', '_')}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "test_type": "direct_cosmos_test",
                "agent_name": "DirectTestAgent",
                "event_type": "direct_insertion_test",
                "data": {
                    "message": "🎯 Testing direct Cosmos DB insertion via MCP",
                    "session_id": session_id,
                    "success": True
                },
                "partition_key": "direct_test"
            }
            
            # Try common Cosmos DB tool names
            tool_names_to_try = [
                "cosmos_db_insert_item",
                "cosmos_db_insert", 
                "insert_document",
                "cosmos_insert",
                "cosmos_db_query_items"
            ]
            
            for tool_name in tool_names_to_try:
                print(f"\n🔍 Trying tool: {tool_name}")
                
                insert_response = await client.post(
                    mcp_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": tool_name,
                            "arguments": {
                                "document": test_document,
                                "database": "playwright_logs",
                                "container": "actions"
                            }
                        }
                    },
                    headers=headers_with_session
                )
                
                print(f"Response status: {insert_response.status_code}")
                print(f"Response: {insert_response.text[:300]}...")
                
                if insert_response.status_code == 200:
                    response_text = insert_response.text
                    if "event: message" in response_text:
                        lines = response_text.split('\n')
                        for line in lines:
                            if line.startswith('data: '):
                                data_json = line[6:]
                                try:
                                    result = json.loads(data_json)
                                    
                                    if "result" in result:
                                        print(f"🎉 SUCCESS with {tool_name}!")
                                        print(f"📄 Document ID: {test_document['id']}")
                                        print(f"📋 Result: {result['result']}")
                                        return True
                                    elif "error" in result:
                                        error = result['error']
                                        if error['code'] == -32601:  # Method not found
                                            print(f"⚠️  Tool {tool_name} not found, trying next...")
                                            continue
                                        else:
                                            print(f"❌ Error with {tool_name}: {error}")
                                            continue
                                except json.JSONDecodeError:
                                    print(f"❌ Invalid JSON response for {tool_name}")
                                    continue
                    
            print("\n❌ None of the tool names worked")
            return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    print("🚀 Testing Direct Cosmos DB Insertion\n")
    
    success = await test_direct_cosmos_insert()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS! Direct Cosmos DB insertion worked!")
        print("✅ Check your Cosmos DB 'actions' container for the test document.")
    else:
        print("❌ Direct Cosmos DB insertion failed.")
        print("💡 The MCP server might use different tool names.")


if __name__ == "__main__":
    asyncio.run(main())
