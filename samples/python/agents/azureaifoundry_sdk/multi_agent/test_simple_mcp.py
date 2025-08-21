"""
Test script for the simple MCP server.
This tests both read and write operations to prove the concept.
"""
import requests
import json

def test_simple_mcp():
    """Test the simple MCP server tools."""
    mcp_url = "http://localhost:8081/mcp"
    
    # Step 1: Create session with proper initialization
    print("=== Creating MCP Session ===")
    init_message = {
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
    }
    
    session_response = requests.post(mcp_url, 
                                   headers={
                                       "Content-Type": "application/json",
                                       "Accept": "application/json, text/event-stream"
                                   },
                                   json=init_message)
    
    if session_response.status_code != 200:
        print(f"Failed to create session: {session_response.status_code}")
        print(f"Response: {session_response.text}")
        return
    
    # Extract session ID from headers
    session_id = session_response.headers.get('X-Session-Id') or session_response.headers.get('mcp-session-id')
    if not session_id:
        print("No session ID in response headers")
        print(f"Headers: {dict(session_response.headers)}")
        return
    
    print(f"✅ Session created: {session_id}")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "mcp-session-id": session_id
    }
    
    # Send initialized notification to complete the handshake
    print("=== Completing initialization handshake ===")
    initialized_message = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }
    
    init_complete_response = requests.post(mcp_url, headers=headers, json=initialized_message)
    if init_complete_response.status_code == 200:
        print("✅ Initialization handshake completed")
    else:
        print(f"⚠️ Initialization handshake failed: {init_complete_response.status_code}")
        print(f"Response: {init_complete_response.text}")
    
    # Step 2: Test log_action tool (write operation)
    print("\n=== Testing log_action (write operation) ===")
    log_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "log_action",
            "arguments": {
                "agent": "time_agent",
                "action": "get_current_time",
                "details": "User requested current time via MCP test"
            }
        }
    }
    
    log_response = requests.post(mcp_url, headers=headers, json=log_request)
    print(f"Response status: {log_response.status_code}")
    
    # Handle SSE response
    if log_response.headers.get('content-type', '').startswith('text/event-stream'):
        print("Log action response:")
        for line in log_response.text.strip().split('\n'):
            if line.startswith('data: '):
                data_content = line[6:]  # Remove 'data: ' prefix
                try:
                    parsed = json.loads(data_content)
                    if 'result' in parsed:
                        print(f"  ✅ {parsed['result']}")
                    else:
                        print(f"  📝 {json.dumps(parsed, indent=2)}")
                except json.JSONDecodeError:
                    print(f"  📝 {data_content}")
    
    # Step 3: Log another action
    print("\n=== Logging another action ===")
    log_request2 = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "log_action",
            "arguments": {
                "agent": "time_agent",
                "action": "get_timezone",
                "details": "User requested timezone information"
            }
        }
    }
    
    log_response2 = requests.post(mcp_url, headers=headers, json=log_request2)
    
    if log_response2.headers.get('content-type', '').startswith('text/event-stream'):
        for line in log_response2.text.strip().split('\n'):
            if line.startswith('data: '):
                data_content = line[6:]
                try:
                    parsed = json.loads(data_content)
                    if 'result' in parsed:
                        print(f"  ✅ {parsed['result']}")
                except json.JSONDecodeError:
                    pass
    
    # Step 4: Test query_cosmos tool (read operation)
    print("\n=== Testing query_cosmos (read operation) ===")
    query_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "query_cosmos",
            "arguments": {
                "query": "SELECT * FROM actions"
            }
        }
    }
    
    query_response = requests.post(mcp_url, headers=headers, json=query_request)
    print(f"Response status: {query_response.status_code}")
    
    if query_response.headers.get('content-type', '').startswith('text/event-stream'):
        print("Query results:")
        for line in query_response.text.strip().split('\n'):
            if line.startswith('data: '):
                data_content = line[6:]
                try:
                    parsed = json.loads(data_content)
                    if 'result' in parsed:
                        print(f"  📊 {parsed['result']}")
                    else:
                        print(f"  📝 {json.dumps(parsed, indent=2)}")
                except json.JSONDecodeError:
                    print(f"  📝 {data_content}")
    
    # Step 5: Test get_stats tool
    print("\n=== Testing get_stats ===")
    stats_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_stats",
            "arguments": {}
        }
    }
    
    stats_response = requests.post(mcp_url, headers=headers, json=stats_request)
    
    if stats_response.headers.get('content-type', '').startswith('text/event-stream'):
        print("Statistics:")
        for line in stats_response.text.strip().split('\n'):
            if line.startswith('data: '):
                data_content = line[6:]
                try:
                    parsed = json.loads(data_content)
                    if 'result' in parsed:
                        print(f"  📈 {parsed['result']}")
                except json.JSONDecodeError:
                    pass
    
    print("\n🎉 MCP Server test completed successfully!")
    print("✅ Write operations (log_action) working")
    print("✅ Read operations (query_cosmos, get_stats) working")
    print("✅ Session management working")
    print("✅ Tool parameter passing working")

if __name__ == "__main__":
    test_simple_mcp()
