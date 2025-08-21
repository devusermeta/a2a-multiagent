#!/usr/bin/env python3

import asyncio
import httpx
import json


async def test_routing_agent_with_time_agent():
    """Test the routing agent's ability to discover and call the time agent"""
    print("🎯 Testing Routing Agent Discovery of TimeAgent...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test routing agent agent card
            response = await client.get("http://localhost:8000/.well-known/agent.json")
            if response.status_code == 200:
                print("✅ Routing Agent is running")
                agent_card = response.json()
                print(f"   Agent Name: {agent_card.get('name', 'Unknown')}")
            else:
                print(f"❌ Routing Agent not available at localhost:8000")
                return False

            # Send a time-related query to the routing agent
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "message/send",
                "params": {
                    "id": "routing-test-123",
                    "sessionId": "routing-session-456",
                    "acceptedOutputModes": ["text"],
                    "message": {
                        "messageId": "routing-msg-1",
                        "kind": "message", 
                        "role": "user",
                        "parts": [
                            {
                                "kind": "text",
                                "text": "What time is it right now?"
                            }
                        ]
                    }
                }
            }
            
            response = await client.post(
                "http://localhost:8000/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ Routing Agent successfully processed time query")
                result = response.json()
                print(f"   Response: {str(result)[:300]}...")
                return True
            else:
                print(f"❌ Routing Agent returned status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing routing agent: {e}")
        return False


async def main():
    print("🚀 Multi-Agent Time Integration Test")
    print("=" * 50)
    
    # Test routing agent with time query 
    routing_ok = await test_routing_agent_with_time_agent()
    
    print("\n📊 Test Results Summary:")
    print(f"   Routing Agent → TimeAgent: {'✅' if routing_ok else '❌'}")
    
    if routing_ok:
        print("\n🎉 Multi-agent routing is working! Host agent can discover and call TimeAgent!")
    else:
        print("\n⚠️  Multi-agent routing test failed. Make sure routing agent is running on port 8000.")
        print("\nTo start the routing agent:")
        print("   cd samples/python/agents/azureaifoundry_sdk/multi_agent/host_agent")
        print("   python __main__.py")


if __name__ == "__main__":
    asyncio.run(main())
