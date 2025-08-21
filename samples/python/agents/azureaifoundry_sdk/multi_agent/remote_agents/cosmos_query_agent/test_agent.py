#!/usr/bin/env python3
"""
Simple test script to verify Cosmos Query Agent MCP functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from agent import CosmosQueryAgent

async def test_cosmos_query_agent():
    """Test the Cosmos Query Agent functionality"""
    
    print("🧪 Testing Cosmos Query Agent...")
    
    # Create agent instance
    agent = CosmosQueryAgent()
    
    # Initialize the agent
    print("\n1. Initializing agent...")
    success = await agent.initialize()
    if not success:
        print("❌ Failed to initialize agent")
        return
    
    print("✅ Agent initialized successfully")
    
    # Test 1: List containers
    print("\n2. Testing: List containers")
    result = await agent.process_query("Show me all containers in the database")
    print(f"Result: {result}")
    
    # Test 2: Query time_agent data
    print("\n3. Testing: Query time_agent data")
    result = await agent.process_query("Show me time_agent entries")
    print(f"Result: {result}")
    
    # Test 3: Count documents
    print("\n4. Testing: Count documents")
    result = await agent.process_query("How many documents are in the actions container?")
    print(f"Result: {result}")
    
    # Test 4: Describe container schema
    print("\n5. Testing: Describe container")
    result = await agent.process_query("Describe the actions container schema")
    print(f"Result: {result}")
    
    # Test 5: Direct SQL query
    print("\n6. Testing: Direct SQL query")
    result = await agent.process_query("SELECT * FROM c WHERE c.agent_name = 'TimeAgent' ORDER BY c._ts DESC")
    print(f"Result: {result}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_cosmos_query_agent())
