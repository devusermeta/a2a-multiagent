#!/usr/bin/env python3

import asyncio
import httpx
import json


async def test_mcp_simple():
    """Simple test to understand MCP server format"""
    print("🧪 Testing MCP Server Basic Connection")
    print("=" * 50)
    
    mcp_url = "http://127.0.0.1:8080/mcp"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            
            print("🔍 Step 1: Basic initialize call...")
            response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "SimpleTestClient",
                            "version": "1.0.0"
                        }
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Raw Response: {response.text[:500]}")
            
            # Check if it's event stream format
            if "text/event-stream" in response.headers.get("content-type", ""):
                print("\n📡 Event Stream Response Detected!")
                lines = response.text.split('\n')
                for i, line in enumerate(lines[:10]):  # First 10 lines
                    print(f"Line {i}: {line}")
            else:
                print("\n📝 JSON Response Detected!")
                try:
                    json_resp = response.json()
                    print(f"JSON: {json.dumps(json_resp, indent=2)}")
                except:
                    print("Could not parse as JSON")
                    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_simple())
