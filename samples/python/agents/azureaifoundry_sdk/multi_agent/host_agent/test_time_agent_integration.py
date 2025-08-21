#!/usr/bin/env python3
"""
Comprehensive test script to verify that the TimeAgent is working correctly
and can be called dynamically by the HostAgent (RoutingAgent).
"""

import asyncio
import os
import json
import httpx
from typing import Dict, Any

from routing_agent import RoutingAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_time_agent_directly():
    """Test the TimeAgent directly by calling its endpoint."""
    print("🧪 Testing TimeAgent directly...")
    
    time_agent_url = os.getenv('TIME_AGENT_URL', 'http://localhost:10003')
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Test 1: Get agent card
            print(f"📋 Getting agent card from {time_agent_url}")
            response = await client.get(f"{time_agent_url}agent_card")
            
            if response.status_code == 200:
                agent_card = response.json()
                print("✅ Agent card retrieved successfully:")
                print(f"  - Name: {agent_card.get('name', 'Unknown')}")
                print(f"  - Description: {agent_card.get('description', 'No description')}")
                print(f"  - Version: {agent_card.get('version', 'Unknown')}")
                print(f"  - Skills: {len(agent_card.get('skills', []))}")
                
                # Show skills
                for skill in agent_card.get('skills', []):
                    print(f"    * {skill.get('name', 'Unknown skill')}: {skill.get('description', 'No description')}")
                    print(f"      Examples: {skill.get('examples', [])}")
                
                return True
            else:
                print(f"❌ Failed to get agent card: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except httpx.ConnectError:
        print(f"❌ Cannot connect to TimeAgent at {time_agent_url}")
        print("Make sure the TimeAgent is running with:")
        print(f"  cd {os.path.dirname(__file__)}/../remote_agents/time_agent")
        print("  python -m uv run python -m time_agent")
        return False
    except Exception as e:
        print(f"❌ Error testing TimeAgent directly: {e}")
        return False


async def test_routing_agent_time_agent_integration():
    """Test that the RoutingAgent can successfully route to and call the TimeAgent."""
    print("\n🤖 Testing RoutingAgent -> TimeAgent integration...")
    
    try:
        # Create routing agent with all three agents
        print("📡 Creating RoutingAgent with all remote agents...")
        routing_agent = await RoutingAgent.create(
            remote_agent_addresses=[
                os.getenv('TOOL_AGENT_URL', 'http://localhost:10002'),
                os.getenv('PLAYWRIGHT_AGENT_URL', 'http://localhost:10001'),
                os.getenv('TIME_AGENT_URL', 'http://localhost:10003'),
            ]
        )
        
        print("✅ RoutingAgent created successfully")
        
        # Check if TimeAgent was discovered
        print("\n🔍 Checking discovered agents...")
        remote_agents = routing_agent.list_remote_agents()
        
        time_agent_found = False
        for agent in remote_agents:
            agent_name = agent.get('name', 'Unknown')
            print(f"  - {agent_name}: {agent.get('description', 'No description')}")
            if 'Time' in agent_name or 'time' in agent_name.lower():
                time_agent_found = True
                print(f"    ✅ TimeAgent found: {agent_name}")
        
        if not time_agent_found:
            print("❌ TimeAgent not found in discovered agents")
            return False
        
        # Create Azure AI agent
        print("\n🤖 Creating Azure AI agent...")
        try:
            azure_agent = routing_agent.create_agent()
            print(f"✅ Azure AI agent created with ID: {azure_agent.id}")
        except Exception as e:
            print(f"❌ Failed to create Azure AI agent: {e}")
            print("This might be due to Azure configuration issues.")
            return False
        
        # Test time-related queries
        time_queries = [
            "What time is it?",
            "What's the current date?",
            "Can you tell me today's date and time?",
            "What day is today?",
            "Show me the current timestamp"
        ]
        
        print("\n⏰ Testing time-related queries...")
        
        for i, query in enumerate(time_queries, 1):
            print(f"\n📝 Test {i}: {query}")
            try:
                response = await routing_agent.process_user_message(query)
                print(f"✅ Response: {response[:200]}...")
                
                # Check if response contains time/date information
                if any(word in response.lower() for word in ['time', 'date', 'today', 'current', 'utc', '2025']):
                    print("✅ Response appears to contain time/date information")
                else:
                    print("⚠️  Response may not contain expected time/date information")
                    
            except Exception as e:
                print(f"❌ Query failed: {e}")
                return False
        
        print("\n🧹 Cleaning up...")
        routing_agent.cleanup()
        print("✅ Integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_time_agent_vs_other_agents():
    """Test that TimeAgent works alongside other agents (tool_agent, playwright_agent)."""
    print("\n🔄 Testing TimeAgent alongside other agents...")
    
    try:
        # Create routing agent
        routing_agent = await RoutingAgent.create(
            remote_agent_addresses=[
                os.getenv('TOOL_AGENT_URL', 'http://localhost:10002'),
                os.getenv('PLAYWRIGHT_AGENT_URL', 'http://localhost:10001'),
                os.getenv('TIME_AGENT_URL', 'http://localhost:10003'),
            ]
        )
        
        # Create Azure AI agent
        azure_agent = routing_agent.create_agent()
        
        # Test queries that should route to different agents
        test_scenarios = [
            {
                "query": "What time is it right now?",
                "expected_agent": "TimeAgent",
                "keywords": ["time", "date", "utc", "current"]
            },
            {
                "query": "Can you help me with a calculation?",
                "expected_agent": "ToolAgent", 
                "keywords": ["calculation", "math", "tool"]
            },
            # Note: Playwright agent might need a website to test properly
        ]
        
        print(f"\n🎯 Testing {len(test_scenarios)} routing scenarios...")
        
        for i, scenario in enumerate(test_scenarios, 1):
            query = scenario["query"]
            expected_agent = scenario["expected_agent"]
            keywords = scenario["keywords"]
            
            print(f"\n📝 Scenario {i}: {query}")
            print(f"   Expected to route to: {expected_agent}")
            
            try:
                response = await routing_agent.process_user_message(query)
                print(f"✅ Response received: {response[:150]}...")
                
                # Check if response contains expected keywords
                response_lower = response.lower()
                keyword_found = any(keyword in response_lower for keyword in keywords)
                
                if keyword_found:
                    print(f"✅ Response contains expected keywords for {expected_agent}")
                else:
                    print(f"⚠️  Response may not be from {expected_agent} (no expected keywords found)")
                    
            except Exception as e:
                print(f"❌ Scenario {i} failed: {e}")
        
        # Cleanup
        routing_agent.cleanup()
        print("\n✅ Multi-agent routing test completed")
        return True
        
    except Exception as e:
        print(f"❌ Multi-agent test failed: {e}")
        return False


async def run_agent_health_check():
    """Run a health check on all configured agents."""
    print("\n🏥 Running health check on all agents...")
    
    agent_urls = {
        'ToolAgent': os.getenv('TOOL_AGENT_URL', 'http://localhost:10002'),
        'PlaywrightAgent': os.getenv('PLAYWRIGHT_AGENT_URL', 'http://localhost:10001'), 
        'TimeAgent': os.getenv('TIME_AGENT_URL', 'http://localhost:10003'),
    }
    
    health_results = {}
    
    for agent_name, url in agent_urls.items():
        print(f"\n🔍 Checking {agent_name} at {url}...")
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Try to get agent card
                response = await client.get(f"{url}agent_card")
                
                if response.status_code == 200:
                    agent_card = response.json()
                    health_results[agent_name] = {
                        'status': 'healthy',
                        'url': url,
                        'name': agent_card.get('name', 'Unknown'),
                        'version': agent_card.get('version', 'Unknown'),
                        'skills': len(agent_card.get('skills', []))
                    }
                    print(f"✅ {agent_name} is healthy")
                    print(f"   Name: {agent_card.get('name', 'Unknown')}")
                    print(f"   Skills: {len(agent_card.get('skills', []))}")
                else:
                    health_results[agent_name] = {
                        'status': 'unhealthy',
                        'url': url,
                        'error': f"HTTP {response.status_code}"
                    }
                    print(f"❌ {agent_name} is unhealthy: HTTP {response.status_code}")
                    
        except httpx.ConnectError:
            health_results[agent_name] = {
                'status': 'unreachable',
                'url': url,
                'error': 'Connection refused'
            }
            print(f"❌ {agent_name} is unreachable at {url}")
        except Exception as e:
            health_results[agent_name] = {
                'status': 'error',
                'url': url,
                'error': str(e)
            }
            print(f"❌ {agent_name} error: {e}")
    
    # Summary
    print("\n📊 Health Check Summary:")
    healthy_count = sum(1 for result in health_results.values() if result['status'] == 'healthy')
    total_count = len(health_results)
    
    print(f"Healthy agents: {healthy_count}/{total_count}")
    
    for agent_name, result in health_results.items():
        status_emoji = "✅" if result['status'] == 'healthy' else "❌"
        print(f"  {status_emoji} {agent_name}: {result['status']}")
    
    return health_results


def print_startup_instructions():
    """Print instructions for starting all agents."""
    print("\n📋 Agent Startup Instructions:")
    print("To start all agents, run these commands in separate terminals:")
    print()
    
    base_path = os.path.dirname(os.path.dirname(__file__))  # Go up to multi_agent directory
    
    agents = [
        ('TimeAgent', 'time_agent', '10003'),
        ('ToolAgent', 'tool_agent', '10002'), 
        ('PlaywrightAgent', 'playwright_agent', '10001'),
    ]
    
    for agent_name, agent_dir, port in agents:
        print(f"🚀 {agent_name} (port {port}):")
        print(f"   cd {base_path}\\remote_agents\\{agent_dir}")
        print(f"   python -m {agent_dir}")
        print()
    
    print("🏠 Host Agent (RoutingAgent):")
    print(f"   cd {base_path}\\host_agent")
    print("   python __main__.py")
    print()


async def main():
    """Main test function."""
    print("🧪 TimeAgent Integration Test Suite")
    print("=" * 50)
    
    # Print startup instructions
    print_startup_instructions()
    
    # Run health check first
    health_results = await run_agent_health_check()
    
    # Count healthy agents
    healthy_agents = [name for name, result in health_results.items() if result['status'] == 'healthy']
    
    if 'TimeAgent' not in healthy_agents:
        print("\n❌ TimeAgent is not running or not healthy.")
        print("Please start the TimeAgent first:")
        print("   cd ../remote_agents/time_agent")
        print("   python -m time_agent")
        return
    
    print(f"\n✅ Found {len(healthy_agents)} healthy agents: {', '.join(healthy_agents)}")
    
    # Test TimeAgent directly
    direct_test_success = await test_time_agent_directly()
    
    if not direct_test_success:
        print("\n❌ TimeAgent direct test failed. Skipping integration tests.")
        return
    
    # Test integration with RoutingAgent
    integration_test_success = await test_routing_agent_time_agent_integration()
    
    if integration_test_success:
        # Test alongside other agents
        await test_time_agent_vs_other_agents()
    
    print("\n🎉 Test suite completed!")
    print("\nSummary:")
    print(f"  ✅ TimeAgent direct test: {'PASSED' if direct_test_success else 'FAILED'}")
    print(f"  ✅ RoutingAgent integration: {'PASSED' if integration_test_success else 'FAILED'}")


if __name__ == "__main__":
    asyncio.run(main())
