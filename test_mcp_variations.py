#!/usr/bin/env python3

import asyncio
import httpx
import json


async def test_mcp_variations():
    """Test various MCP call variations"""
    print("🧪 Testing MCP Variations")
    print("=" * 50)
    
    mcp_url = "http://127.0.0.1:8080/mcp"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            
            # Step 1: Initialize 
            print("🔍 Step 1: Initialize...")
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
                            "name": "VariationTestClient",
                            "version": "1.0.0"
                        }
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            session_id = response.headers.get('mcp-session-id')
            print(f"✅ Session ID: {session_id}")
            
            # Step 2: Try different tools/list variations
            print(f"\n🔍 Step 2: Try different tools/list variations...")
            
            variations = [
                {"method": "tools/list", "params": {}},
                {"method": "tools/list"},
                {"method": "tools/list", "params": None},
                {"method": "listTools", "params": {}},
                {"method": "listTools"},
            ]
            
            for i, variation in enumerate(variations, 1):
                print(f"  Variation {i}: {variation}")
                try:
                    tools_response = await client.post(
                        mcp_url,
                        json={
                            "jsonrpc": "2.0",
                            "id": i + 10,
                            **variation
                        },
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json, text/event-stream",
                            "mcp-session-id": session_id
                        }
                    )
                    
                    print(f"    Status: {tools_response.status_code}")
                    result_preview = tools_response.text[:150].replace('\n', ' ')
                    print(f"    Preview: {result_preview}...")
                    
                    if tools_response.status_code == 200 and "error" not in tools_response.text:
                        print(f"    ✅ SUCCESS with variation {i}!")
                        
                        # Try to parse the tools
                        if "event: message" in tools_response.text:
                            lines = tools_response.text.split('\n')
                            for line in lines:
                                if line.startswith('data: '):
                                    data_json = line[6:]
                                    result = json.loads(data_json)
                                    if "result" in result and "tools" in result["result"]:
                                        tools = result["result"]["tools"]
                                        print(f"    ✅ Found {len(tools)} tools!")
                                        for tool in tools[:3]:  # Show first 3
                                            print(f"      - {tool['name']}")
                                        return tools
                        
                except Exception as e:
                    print(f"    ❌ Exception: {e}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_variations())
