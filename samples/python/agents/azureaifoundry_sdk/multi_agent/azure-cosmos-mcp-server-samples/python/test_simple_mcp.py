#!/usr/bin/env python3
"""
Super simple test to check what tools are available from the MCP server.
This bypasses session management issues and just tests basic connectivity.
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def simple_mcp_test():
    """Simple test to see what the MCP server responds with."""
    print("🧪 Simple MCP Server Connectivity Test")
    
    mcp_url = f"http://{os.getenv('MCP_HOST', '127.0.0.1')}:{os.getenv('MCP_PORT', '8080')}/mcp"
    print(f"📡 Testing {mcp_url}")
    
    # Try different approaches to connect
    headers_variants = [
        {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        {
            "Accept": "application/json, text/event-stream", 
            "Content-Type": "application/json"
        },
        {
            "Accept": "*/*",
            "Content-Type": "application/json"
        }
    ]
    
    methods_to_try = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        },
        {
            "jsonrpc": "2.0", 
            "id": 1,
            "method": "tools/list"
        }
    ]
    
    async with httpx.AsyncClient(timeout=30) as client:
        for i, headers in enumerate(headers_variants):
            print(f"\n🔍 Attempt {i+1}: Testing headers {headers}")
            
            for j, method_call in enumerate(methods_to_try):
                print(f"   Method variant {j+1}: {method_call['method']}")
                
                try:
                    response = await client.post(mcp_url, json=method_call, headers=headers)
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"   ✅ SUCCESS! Response: {json.dumps(data, indent=2)}")
                            return True
                        except:
                            print(f"   Response text: {response.text[:200]}...")
                    else:
                        print(f"   Response: {response.text[:200]}...")
                        
                except Exception as e:
                    print(f"   Error: {e}")
    
    print("\n❌ All attempts failed")
    return False

if __name__ == "__main__":
    asyncio.run(simple_mcp_test())
