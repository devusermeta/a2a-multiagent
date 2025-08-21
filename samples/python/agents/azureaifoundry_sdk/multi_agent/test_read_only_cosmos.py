"""
Test script for the read-only Cosmos DB MCP server tools.
"""
import requests
import json

def test_cosmos_query():
    """Test the query_cosmos tool with proper parameters."""
    mcp_url = "http://localhost:8080/mcp"
    
    # Step 1: Create session
    session_response = requests.post(mcp_url, 
                                   headers={"Content-Type": "application/json"},
                                   json={})
    
    if session_response.status_code != 200:
        print(f"Failed to create session: {session_response.status_code}")
        print(f"Response: {session_response.text}")
        return
    
    # Extract session ID from headers
    session_id = session_response.headers.get('X-Session-Id')
    if not session_id:
        print("No session ID in response headers")
        print(f"Headers: {dict(session_response.headers)}")
        return
    
    print(f"Session created: {session_id}")
    
    # Step 2: Use query_cosmos tool (one of the actual available tools)
    tool_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "query_cosmos",
            "arguments": {
                "query": "SELECT TOP 5 * FROM c"
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Session-Id": session_id
    }
    
    print(f"Calling query_cosmos tool...")
    tool_response = requests.post(mcp_url, headers=headers, json=tool_request)
    
    print(f"Response status: {tool_response.status_code}")
    print(f"Response headers: {dict(tool_response.headers)}")
    
    # Handle SSE response
    if tool_response.headers.get('content-type', '').startswith('text/event-stream'):
        print("SSE Response content:")
        for line in tool_response.text.strip().split('\n'):
            if line.startswith('data: '):
                data_content = line[6:]  # Remove 'data: ' prefix
                try:
                    parsed = json.loads(data_content)
                    print(f"  {json.dumps(parsed, indent=2)}")
                except json.JSONDecodeError:
                    print(f"  {data_content}")
            elif line.strip():
                print(f"  {line}")
    else:
        try:
            response_json = tool_response.json()
            print(f"JSON Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Raw response: {tool_response.text}")

def test_list_collections():
    """Test the list_collections tool."""
    mcp_url = "http://localhost:8080/mcp"
    
    # Step 1: Create session
    session_response = requests.post(mcp_url, 
                                   headers={"Content-Type": "application/json"},
                                   json={})
    
    session_id = session_response.headers.get('X-Session-Id')
    if not session_id:
        print("No session ID in response headers")
        return
    
    print(f"Session created: {session_id}")
    
    # Step 2: Use list_collections tool
    tool_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "list_collections",
            "arguments": {}
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Session-Id": session_id
    }
    
    print(f"Calling list_collections tool...")
    tool_response = requests.post(mcp_url, headers=headers, json=tool_request)
    
    print(f"Response status: {tool_response.status_code}")
    
    # Handle SSE response
    if tool_response.headers.get('content-type', '').startswith('text/event-stream'):
        print("SSE Response content:")
        for line in tool_response.text.strip().split('\n'):
            if line.startswith('data: '):
                data_content = line[6:]  # Remove 'data: ' prefix
                try:
                    parsed = json.loads(data_content)
                    print(f"  {json.dumps(parsed, indent=2)}")
                except json.JSONDecodeError:
                    print(f"  {data_content}")
            elif line.strip():
                print(f"  {line}")
    else:
        try:
            response_json = tool_response.json()
            print(f"JSON Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Raw response: {tool_response.text}")

if __name__ == "__main__":
    print("=== Testing query_cosmos tool ===")
    test_cosmos_query()
    
    print("\n=== Testing list_collections tool ===")
    test_list_collections()
