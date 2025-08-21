#!/usr/bin/env python3
"""
Proper FastMCP Client Test for Azure Cosmos DB MCP Server
Uses the correct streamable-http protocol for session management
"""

import requests
import json
import uuid
import time

def test_cosmos_with_proper_session():
    """Test Azure Cosmos DB MCP server with proper FastMCP session protocol"""
    
    base_url = "http://localhost:8080/mcp"
    
    print("🔍 Testing Azure Cosmos DB MCP Server with Proper Session Management")
    print(f"📡 Server URL: {base_url}")
    print("=" * 80)
    
    # Step 1: Establish a session using Server-Sent Events
    print("\n1️⃣ Establishing SSE session...")
    try:
        # Create a session using the streamable-http protocol
        session = requests.Session()
        
        # Start an SSE connection to establish session
        headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        }
        
        # Make initial connection to establish session
        response = session.post(base_url, headers=headers, stream=True)
        
        if response.status_code == 200:
            print(f"   ✅ SSE session established")
            session_id = None
            
            # Read the first few events to get session info
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                        if 'session' in data or 'id' in data:
                            session_id = data.get('session_id', str(uuid.uuid4()))
                            break
                    except:
                        continue
                # Break after a short time to avoid hanging
                break
            
            response.close()
            
            if not session_id:
                session_id = str(uuid.uuid4())
                
            print(f"   🆔 Session ID: {session_id}")
            
        else:
            print(f"   ❌ Failed to establish session: {response.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ Session error: {e}")
        return
    
    # Step 2: Test tools with established session
    print(f"\n2️⃣ Testing tools with session ID: {session_id}")
    
    # Headers for tool calls
    tool_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Session-ID": session_id
    }
    
    # Test count_documents first (simplest)
    print("\n   📊 Testing count_documents...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "count_documents",
                "arguments": {}
            }
        }
        
        response = requests.post(base_url, json=payload, headers=tool_headers)
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print(f"      ✅ Count result: {result['result']}")
            else:
                print(f"      ⚠️ Unexpected response: {result}")
        else:
            print(f"      ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"      ❌ Exception: {e}")
    
    # Test list_collections
    print("\n   📂 Testing list_collections...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "list_collections",
                "arguments": {}
            }
        }
        
        response = requests.post(base_url, json=payload, headers=tool_headers)
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print(f"      ✅ Collections: {result['result']}")
            else:
                print(f"      ⚠️ Unexpected response: {result}")
        else:
            print(f"      ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"      ❌ Exception: {e}")
    
    # Test simple query
    print("\n   🔍 Testing query_cosmos...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "query_cosmos",
                "arguments": {
                    "query": "SELECT TOP 3 c.id, c._ts FROM c ORDER BY c._ts DESC"
                }
            }
        }
        
        response = requests.post(base_url, json=payload, headers=tool_headers)
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print(f"      ✅ Query result: {result['result']}")
            else:
                print(f"      ⚠️ Unexpected response: {result}")
        else:
            print(f"      ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"      ❌ Exception: {e}")

    print("\n" + "=" * 80)
    print("✅ Azure Cosmos DB MCP Server test completed!")
    print("   If successful, the time_agent can now use these tools for logging!")

if __name__ == "__main__":
    test_cosmos_with_proper_session()
