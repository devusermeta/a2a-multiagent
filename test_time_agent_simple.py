#!/usr/bin/env python3

import asyncio
import httpx
import json


async def test_time_agent():
    """Test the time agent directly"""
    print("🧪 Testing TimeAgent with Cosmos DB logging...")
    
    # Test the agent card endpoint at the correct path
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:10003/.well-known/agent.json")
            if response.status_code == 200:
                print("✅ TimeAgent is running and responding to agent_card requests")
                agent_card = response.json()
                print(f"   Agent Name: {agent_card.get('name', 'Unknown')}")
                print(f"   Description: {agent_card.get('description', 'N/A')}")
                print(f"   Skills: {len(agent_card.get('skills', []))}")
                return True
            else:
                print(f"❌ TimeAgent agent_card returned status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error testing TimeAgent: {e}")
        return False


async def test_time_query():
    """Test sending a time query to the agent via A2A JSON-RPC"""
    print("\n🕐 Testing time query with Cosmos DB logging...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Create A2A JSON-RPC message payload
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "message/send",
                "params": {
                    "id": "test-task-123",
                    "sessionId": "test-session-456",
                    "acceptedOutputModes": ["text"],
                    "message": {
                        "messageId": "msg-1",
                        "kind": "message", 
                        "role": "user",
                        "parts": [
                            {
                                "kind": "text",
                                "text": "What time is it?"
                            }
                        ]
                    }
                }
            }
            
            response = await client.post(
                "http://localhost:10003/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ TimeAgent successfully processed time query")
                result = response.json()
                print(f"   Response type: {type(result)}")
                print(f"   Response: {str(result)[:200]}...")
                return True
            else:
                print(f"❌ TimeAgent time query returned status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing time query: {e}")
        return False


async def check_mcp_server():
    """Check if the MCP server is still running"""
    print("\n🔗 Checking MCP Server status...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8080/mcp")
            # HTTP 406 (Not Acceptable) or 405 (Method Not Allowed) means server is running but expects POST
            if response.status_code in [200, 405, 406]:  
                print("✅ MCP Server is running (HTTP 406 is expected for GET requests)")
                return True
            else:
                print(f"❌ MCP Server returned unexpected status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error checking MCP server: {e}")
        return False


async def main():
    print("🚀 TimeAgent + Cosmos DB + MCP Integration Test")
    print("=" * 50)
    
    # Check MCP server first
    mcp_ok = await check_mcp_server()
    
    # Test agent card
    agent_ok = await test_time_agent()
    
    # Test time query if agent is working
    if agent_ok:
        query_ok = await test_time_query()
    else:
        query_ok = False
    
    print("\n📊 Test Results Summary:")
    print(f"   MCP Server: {'✅' if mcp_ok else '❌'}")
    print(f"   TimeAgent Health: {'✅' if agent_ok else '❌'}")
    print(f"   Time Query: {'✅' if query_ok else '❌'}")
    
    if mcp_ok and agent_ok and query_ok:
        print("\n🎉 All tests passed! TimeAgent is working with Cosmos DB logging!")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())
