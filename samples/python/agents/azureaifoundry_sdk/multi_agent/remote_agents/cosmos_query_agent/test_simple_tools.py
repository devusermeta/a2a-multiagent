#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from agent import CosmosQueryAgent

async def test_simple_tools():
    """Test simple tools individually"""
    
    print("🧪 Testing Individual Tools...")
    
    # Create agent instance
    agent = CosmosQueryAgent()
    
    # Initialize the agent
    print("\n1. Initializing agent...")
    success = await agent.initialize()
    if not success:
        print("❌ Failed to initialize agent")
        return
    
    print("✅ Agent initialized successfully")
    
    # Test 1: List containers (no parameters)
    print("\n2. Testing: list_collections (no parameters)")
    result = await agent._call_mcp_tool("list_collections")
    print(f"Result: {result}")
    
    # Test 2: Count documents (no parameters)  
    print("\n3. Testing: count_documents (no parameters)")
    result = await agent._call_mcp_tool("count_documents")
    print(f"Result: {result}")
    
    # Test 3: Query cosmos with a simple query
    print("\n4. Testing: query_cosmos with simple query")
    result = await agent._call_mcp_tool("query_cosmos", {"query": "SELECT * FROM c OFFSET 0 LIMIT 3"})
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_simple_tools())
