#!/usr/bin/env python3
"""
Test script for Azure Cosmos DB MCP Server
Tests tool listing and basic operations
"""

import json
import requests
import time

def test_cosmos_mcp_server():
    """Test the Azure Cosmos DB MCP server functionality"""
    
    base_url = "http://localhost:8080/mcp"
    
    print("🔍 Testing Azure Cosmos DB MCP Server...")
    print(f"📡 Server URL: {base_url}")
    print("-" * 60)
    
    # Headers for FastMCP streamable-http
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    
    # Step 1: List available tools
    print("1️⃣ Listing available tools...")
    try:
        tools_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        tools_response = requests.post(base_url, json=tools_payload, headers=headers)
        print(f"   Status: {tools_response.status_code}")
        
        if tools_response.status_code == 200:
            tools_result = tools_response.json()
            print(f"   ✅ Raw response: {json.dumps(tools_result, indent=2)}")
            
            # Extract and display tools
            if "result" in tools_result and "tools" in tools_result["result"]:
                tools = tools_result["result"]["tools"]
                print(f"\n   📋 Available tools ({len(tools)}):")
                for i, tool in enumerate(tools, 1):
                    name = tool.get("name", "Unknown")
                    description = tool.get("description", "No description")
                    print(f"      {i}. {name}: {description}")
                    
                return tools  # Return tools for further testing
            else:
                print("   ⚠️ No tools found in response")
                return []
        else:
            print(f"   ❌ Failed to list tools: {tools_response.text}")
            return []
            
    except Exception as e:
        print(f"   ❌ Error listing tools: {e}")
        return []

def test_cosmos_tools():
    """Test specific Cosmos DB tools"""
    
    base_url = "http://localhost:8080/mcp"
    headers = {
        "Accept": "application/json, text/event-stream", 
        "Content-Type": "application/json"
    }
    
    print("\n2️⃣ Testing Cosmos DB tools...")
    
    # Test list_collections
    print("\n   📦 Testing list_collections...")
    try:
        collections_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "list_collections",
                "arguments": {}
            }
        }
        
        response = requests.post(base_url, json=collections_payload, headers=headers)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text}")
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    # Test count_documents
    print("\n   🔢 Testing count_documents...")
    try:
        count_payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "count_documents",
                "arguments": {}
            }
        }
        
        response = requests.post(base_url, json=count_payload, headers=headers)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text}")
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    # Test simple query
    print("\n   🔍 Testing query_cosmos...")
    try:
        query_payload = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "query_cosmos",
                "arguments": {
                    "query": "SELECT TOP 5 * FROM c"
                }
            }
        }
        
        response = requests.post(base_url, json=query_payload, headers=headers)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text}")
        
    except Exception as e:
        print(f"      ❌ Error: {e}")

if __name__ == "__main__":
    # First test tool listing
    tools = test_cosmos_mcp_server()
    
    # If tools were found, test them
    if tools:
        test_cosmos_tools()
    
    print("\n" + "=" * 60)
    print("✅ Azure Cosmos DB MCP Server test completed!")
