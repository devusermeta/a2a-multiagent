#!/usr/bin/env python3
"""
Test Azure Cosmos DB MCP Server Tools
This script properly handles FastMCP session management to test read-only Cosmos DB operations
"""

import requests
import json
import uuid

def create_mcp_session():
    """Create a proper MCP session for FastMCP streamable-http"""
    session_id = str(uuid.uuid4())
    return session_id

def test_cosmos_tools():
    """Test the read-only tools in Azure Cosmos DB MCP server"""
    
    base_url = "http://localhost:8080/mcp"
    session_id = create_mcp_session()
    
    print("🔍 Testing Azure Cosmos DB MCP Server Tools")
    print(f"📡 Server URL: {base_url}")
    print(f"🆔 Session ID: {session_id}")
    print("=" * 70)
    
    # Headers with session ID
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "X-Session-ID": session_id
    }
    
    # Test 1: List Collections
    print("\n1️⃣ Testing list_collections...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "list_collections",
                "arguments": {}
            }
        }
        
        response = requests.post(base_url, json=payload, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Collections: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Count Documents  
    print("\n2️⃣ Testing count_documents...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "count_documents",
                "arguments": {}
            }
        }
        
        response = requests.post(base_url, json=payload, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Document count: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Describe Container
    print("\n3️⃣ Testing describe_container...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "describe_container",
                "arguments": {}
            }
        }
        
        response = requests.post(base_url, json=payload, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Container schema: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Get Sample Documents
    print("\n4️⃣ Testing get_sample_documents...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_sample_documents",
                "arguments": {
                    "limit": 3
                }
            }
        }
        
        response = requests.post(base_url, json=payload, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Sample documents: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 5: Simple Query
    print("\n5️⃣ Testing query_cosmos...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "query_cosmos",
                "arguments": {
                    "query": "SELECT TOP 5 c.id, c._ts FROM c ORDER BY c._ts DESC"
                }
            }
        }
        
        response = requests.post(base_url, json=payload, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Query results: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 6: Get Partition Key Info
    print("\n6️⃣ Testing get_partition_key_info...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "get_partition_key_info",
                "arguments": {}
            }
        }
        
        response = requests.post(base_url, json=payload, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Partition key info: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

    print("\n" + "=" * 70)
    print("🎯 Azure Cosmos DB MCP Server Test Summary:")
    print("   - Database: playwright_logs")
    print("   - Container: actions") 
    print("   - These are the tools available for the time_agent to use!")
    print("=" * 70)

if __name__ == "__main__":
    test_cosmos_tools()
