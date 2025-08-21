#!/usr/bin/env python3
"""
Test script to verify the Azure Cosmos DB MCP Server is working correctly.
Run this after setting up your .env file with proper Cosmos DB credentials.
"""

import asyncio
import httpx
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def test_mcp_server():
    """Test the MCP server functionality."""
    print("🧪 Testing Azure Cosmos DB MCP Server...")
    
    # MCP server URL (without trailing slash)
    mcp_url = f"http://{os.getenv('MCP_HOST', '127.0.0.1')}:{os.getenv('MCP_PORT', '8080')}/mcp"
    
    print(f"📡 Testing connection to {mcp_url}")
    
    # Headers required for FastMCP Streamable HTTP transport
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Test 1: Initialize a session first
            print("\n1️⃣ Initializing MCP session...")
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
                            "name": "test-client",
                            "version": "1.0.0"
                        }
                    }
                },
                headers=headers
            )
            
            if init_response.status_code == 200:
                init_data = init_response.json()
                print("✅ MCP session initialized successfully")
                print(f"   Server capabilities: {init_data.get('result', {}).get('capabilities', {})}")
                
                # Get session ID from headers or response
                session_id = init_response.headers.get('x-session-id')
                if session_id:
                    print(f"   Session ID: {session_id}")
                    headers['x-session-id'] = session_id
                
            else:
                print(f"❌ Failed to initialize session: HTTP {init_response.status_code}")
                print(f"Response: {init_response.text}")
                return
            
            # Test 2: List available tools
            print("\n2️⃣ Listing available MCP tools...")
            tools_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                },
                headers=headers
            )
            
            if tools_response.status_code == 200:
                tools_data = tools_response.json()
                if "result" in tools_data and "tools" in tools_data["result"]:
                    tools = tools_data["result"]["tools"]
                    print(f"✅ Found {len(tools)} MCP tools:")
                    for tool in tools:
                        print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                else:
                    print("⚠️  Unexpected tools response format")
                    print(f"Response: {tools_data}")
            else:
                print(f"❌ Failed to list tools: HTTP {tools_response.status_code}")
                print(f"Response: {tools_response.text}")
            
            # Test 3: Test a simple Cosmos DB operation (if tools are available)
            print("\n3️⃣ Testing Cosmos DB connection...")
            if tools_response.status_code == 200:
                test_query_response = await client.post(
                    mcp_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {
                            "name": "cosmos_db_query_items",
                            "arguments": {
                                "query": "SELECT COUNT(1) as count FROM c",
                                "database": os.getenv('COSMOS_DATABASE', 'playwright_logs'),
                                "container": os.getenv('COSMOS_CONTAINER', 'actions')
                            }
                        }
                    },
                    headers=headers
                )
                
                if test_query_response.status_code == 200:
                    query_data = test_query_response.json()
                    print("✅ Cosmos DB connection test successful")
                    print(f"   Query result: {query_data}")
                else:
                    print(f"⚠️  Cosmos DB test failed: HTTP {test_query_response.status_code}")
                    print(f"   Response: {test_query_response.text}")
            
    except httpx.ConnectError:
        print(f"❌ Cannot connect to MCP server at {mcp_url}")
        print("Make sure the MCP server is running with:")
        print("  python cosmos_server.py")
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")

async def test_insert_sample_data():
    """Test inserting sample data to Cosmos DB via MCP."""
    print("\n🔄 Testing data insertion...")
    
    mcp_url = f"http://{os.getenv('MCP_HOST', '127.0.0.1')}:{os.getenv('MCP_PORT', '8080')}/mcp"
    
    # Headers required for FastMCP Streamable HTTP transport
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    
    sample_document = {
        "id": "test-document-001",
        "timestamp": "2025-08-21T09:00:00Z",
        "agent_name": "TestAgent",
        "event_type": "test_event",
        "data": {
            "message": "This is a test log entry",
            "success": True
        },
        "partition_key": "test_agent"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Initialize session first
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
                            "name": "test-client-insert",
                            "version": "1.0.0"
                        }
                    }
                },
                headers=headers
            )
            
            if init_response.status_code != 200:
                print(f"❌ Failed to initialize session for insert test")
                return
                
            # Get session ID
            session_id = init_response.headers.get('x-session-id')
            if session_id:
                headers['x-session-id'] = session_id
            
            insert_response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "cosmos_db_insert_item",
                        "arguments": {
                            "document": sample_document,
                            "database": os.getenv('COSMOS_DATABASE', 'playwright_logs'),
                            "container": os.getenv('COSMOS_CONTAINER', 'actions')
                        }
                    }
                },
                headers=headers
            )
            
            if insert_response.status_code == 200:
                insert_data = insert_response.json()
                print("✅ Sample data inserted successfully")
                print(f"   Insert result: {insert_data}")
            else:
                print(f"❌ Failed to insert sample data: HTTP {insert_response.status_code}")
                print(f"   Response: {insert_response.text}")
                
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")

if __name__ == "__main__":
    print("🚀 Azure Cosmos DB MCP Server Test Suite")
    print("=" * 50)
    
    # Check environment variables
    cosmos_uri = os.getenv('COSMOS_URI')
    cosmos_key = os.getenv('COSMOS_KEY')
    
    if not cosmos_uri or cosmos_uri == 'https://your-account.documents.azure.com:443/':
        print("❌ Please update your .env file with actual Cosmos DB credentials")
        print("   COSMOS_URI=https://your-account.documents.azure.com:443/")
        print("   COSMOS_KEY=your-primary-key")
        exit(1)
    
    if not cosmos_key or cosmos_key == 'your-primary-key':
        print("❌ Please update your .env file with actual Cosmos DB credentials")
        print("   COSMOS_KEY=your-primary-key")
        exit(1)
    
    print("✅ Environment variables configured")
    print(f"   Database: {os.getenv('COSMOS_DATABASE', 'agent_logs')}")
    print(f"   Container: {os.getenv('COSMOS_CONTAINER', 'time_agent_logs')}")
    
    asyncio.run(test_mcp_server())
    asyncio.run(test_insert_sample_data())
