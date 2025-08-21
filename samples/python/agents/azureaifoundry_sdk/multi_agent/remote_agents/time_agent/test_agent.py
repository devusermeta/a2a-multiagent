#!/usr/bin/env python3
"""
Simple test script for the TimeAgent to verify it's working correctly.
"""

import asyncio
import json
from agent import TimeAgentWithCosmosLogging


async def test_time_agent():
    """Test the TimeAgent functionality."""
    print("🧪 Testing TimeAgent functionality...")
    
    # Create and initialize the agent
    agent = TimeAgentWithCosmosLogging()
    
    print("🔧 Initializing TimeAgent...")
    success = await agent.initialize()
    
    if not success:
        print("❌ Failed to initialize TimeAgent")
        return False
    
    print("✅ TimeAgent initialized successfully")
    
    # Test different query types
    test_queries = [
        "What time is it?",
        "What's the current date?", 
        "Give me the current date and time",
        "What day is today?",
        "Show me the timestamp",
        "Random query that should default to datetime info"
    ]
    
    print("\n⏰ Testing query processing...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: '{query}'")
        try:
            response = await agent.process_query(query)
            print(f"✅ Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Test individual methods
    print("\n🔧 Testing individual methods...")
    
    try:
        print("\n📅 Testing get_current_date()...")
        date_info = await agent.get_current_date()
        print(f"✅ Date info: {json.dumps(date_info, indent=2)}")
        
        print("\n⏰ Testing get_current_time()...")
        time_info = await agent.get_current_time()
        print(f"✅ Time info: {json.dumps(time_info, indent=2)}")
        
        print("\n📊 Testing get_datetime_info()...")
        datetime_info = await agent.get_datetime_info()
        print(f"✅ DateTime info: {json.dumps(datetime_info, indent=2)}")
        
    except Exception as e:
        print(f"❌ Method test failed: {e}")
        return False
    
    print("\n✅ All TimeAgent tests passed!")
    return True


if __name__ == "__main__":
    asyncio.run(test_time_agent())
