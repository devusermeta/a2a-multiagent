#!/usr/bin/env python3

import asyncio
import httpx
import json
from datetime import datetime


async def debug_tool_call():
    """Debug what's being sent in tool calls"""
    print("🧪 Debugging Tool Call Format")
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
                            "name": "DebugClient",
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
            
            # Step 2: Try different tool call formats
            print(f"\n🔍 Step 2: Testing different tool call formats...")
            
            test_cases = [
                {
                    "name": "Case 1: list_collections with empty args",
                    "data": {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {
                            "name": "list_collections",
                            "arguments": {}
                        }
                    }
                },
                {
                    "name": "Case 2: list_collections with no arguments field",
                    "data": {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "list_collections"
                        }
                    }
                },
                {
                    "name": "Case 3: query_cosmos with arguments",
                    "data": {
                        "jsonrpc": "2.0",
                        "id": 4,
                        "method": "tools/call",
                        "params": {
                            "name": "query_cosmos",
                            "arguments": {
                                "query": "SELECT * FROM c OFFSET 0 LIMIT 1"
                            }
                        }
                    }
                }
            ]
            
            for test_case in test_cases:
                print(f"\n  {test_case['name']}:")
                print(f"  Sending: {json.dumps(test_case['data'], indent=2)}")
                
                try:
                    tool_response = await client.post(
                        mcp_url,
                        json=test_case['data'],
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json, text/event-stream",
                            "mcp-session-id": session_id
                        }
                    )
                    
                    print(f"  Status: {tool_response.status_code}")
                    print(f"  Response: {tool_response.text}")
                    
                    if tool_response.status_code == 200 and "error" not in tool_response.text:
                        print(f"  ✅ SUCCESS!")
                        break
                    else:
                        print(f"  ❌ Failed")
                        
                except Exception as e:
                    print(f"  ❌ Exception: {e}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(debug_tool_call())
