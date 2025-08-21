#!/usr/bin/env python3
"""
Simple test script for Azure Cosmos DB MCP Server using mcp client library.
This approach uses the official MCP client which handles session management automatically.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mcp_with_native_client():
    """Test MCP server using the native MCP client library."""
    print("🧪 Testing Azure Cosmos DB MCP Server with native MCP client...")
    
    try:
        # Import the MCP client
        from mcp import ClientSession
        from mcp.client.streamable_http import StreamableHTTPTransport
        
        # Create transport
        mcp_url = f"http://{os.getenv('MCP_HOST', '127.0.0.1')}:{os.getenv('MCP_PORT', '8080')}/mcp"
        transport = StreamableHTTPTransport(mcp_url)
        
        print(f"📡 Connecting to MCP server at {mcp_url}")
        
        async with ClientSession(transport) as session:
            print("✅ Connected to MCP server")
            
            # Initialize the connection
            await session.initialize()
            print("✅ Session initialized")
            
            # List available tools
            print("\n📋 Listing available tools...")
            tools = await session.list_tools()
            
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")
            
            # Test a Cosmos DB query
            print("\n🔍 Testing Cosmos DB query...")
            
            # Find the query tool
            query_tool = None
            for tool in tools:
                if "query" in tool.name.lower():
                    query_tool = tool
                    break
            
            if query_tool:
                result = await session.call_tool(
                    query_tool.name,
                    {
                        "query": "SELECT COUNT(1) as count FROM c",
                        "database": os.getenv('COSMOS_DATABASE', 'playwright_logs'),
                        "container": os.getenv('COSMOS_CONTAINER', 'actions')
                    }
                )
                print(f"✅ Query successful: {result}")
            else:
                print("⚠️  No query tool found")
            
            # Test data insertion
            print("\n💾 Testing data insertion...")
            
            # Find the insert tool
            insert_tool = None
            for tool in tools:
                if "insert" in tool.name.lower():
                    insert_tool = tool
                    break
            
            if insert_tool:
                test_document = {
                    "id": "test-from-native-client",
                    "timestamp": "2025-08-21T15:00:00Z",
                    "agent_name": "NativeClientTest",
                    "event_type": "mcp_test",
                    "data": {
                        "message": "Test from native MCP client",
                        "success": True
                    },
                    "partition_key": "test_agent"
                }
                
                result = await session.call_tool(
                    insert_tool.name,
                    {
                        "document": test_document,
                        "database": os.getenv('COSMOS_DATABASE', 'playwright_logs'),
                        "container": os.getenv('COSMOS_CONTAINER', 'actions')
                    }
                )
                print(f"✅ Insert successful: {result}")
            else:
                print("⚠️  No insert tool found")
                
    except ImportError:
        print("❌ MCP client library not available. Installing...")
        print("Run: pip install mcp")
        return False
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Azure Cosmos DB MCP Server Native Client Test")
    print("=" * 50)
    
    # Check environment variables
    cosmos_uri = os.getenv('COSMOS_URI')
    cosmos_key = os.getenv('COSMOS_KEY')
    
    if not cosmos_uri or 'your-account' in cosmos_uri:
        print("❌ Please update your .env file with actual Cosmos DB credentials")
        exit(1)
    
    if not cosmos_key or 'your-primary-key' in cosmos_key:
        print("❌ Please update your .env file with actual Cosmos DB credentials")
        exit(1)
    
    print("✅ Environment variables configured")
    print(f"   Database: {os.getenv('COSMOS_DATABASE', 'playwright_logs')}")
    print(f"   Container: {os.getenv('COSMOS_CONTAINER', 'actions')}")
    
    asyncio.run(test_mcp_with_native_client())
