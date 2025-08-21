import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)
load_dotenv()


class CosmosQueryAgent:
    """
    A specialized agent that uses the Azure Cosmos DB MCP Server to query and explore Cosmos DB data.
    
    This agent provides a natural language interface to interact with Cosmos DB through the MCP server,
    offering capabilities like querying, schema inspection, and data exploration.
    """

    def __init__(self):
        # MCP Server configuration
        self.mcp_server_url = os.getenv('MCP_SERVER_URL', 'http://127.0.0.1:8080/mcp')
        self.cosmos_database = os.getenv('COSMOS_DATABASE', 'playwright_logs')
        self.cosmos_container = os.getenv('COSMOS_CONTAINER', 'actions')
        
        # MCP client session
        self.mcp_session = None
        self.available_tools = []

    async def initialize(self):
        """Initialize the Cosmos Query Agent with MCP server connection."""
        try:
            logger.info("Initializing Cosmos Query Agent with MCP server")
            logger.info(f"MCP Server URL: {self.mcp_server_url}")
            logger.info(f"Target Database: {self.cosmos_database}")
            logger.info(f"Default Container: {self.cosmos_container}")
            
            # Test MCP server connection
            await self._test_mcp_connection()
            
            logger.info("✅ Cosmos Query Agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos Query Agent: {e}")
            return False

    async def _test_mcp_connection(self):
        """Test connection to the MCP server and get available tools."""
        try:
            async with httpx.AsyncClient() as client:
                # Test if MCP server is reachable
                response = await client.get(self.mcp_server_url.replace('/mcp', '/health'), timeout=5.0)
                if response.status_code == 200:
                    logger.info("✅ MCP server is reachable")
                else:
                    logger.warning(f"MCP server returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not test MCP server health endpoint: {e}")
            # Continue anyway as the health endpoint might not exist

    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool result as string
        """
        if arguments is None:
            arguments = {}
            
        try:
            async with httpx.AsyncClient() as client:
                request_data = {
                    "jsonrpc": "2.0",
                    "id": f"tool_call_{datetime.now().isoformat()}",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
                
                response = await client.post(
                    self.mcp_server_url,
                    json=request_data,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        return result["result"].get("content", [{}])[0].get("text", "No result")
                    elif "error" in result:
                        return f"Error: {result['error'].get('message', 'Unknown error')}"
                    else:
                        return "Unknown response format"
                else:
                    return f"HTTP Error {response.status_code}: {response.text}"
                    
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return f"Error calling tool: {str(e)}"

    async def query_cosmos_db(self, query: str) -> str:
        """
        Execute a SQL-like query on the Cosmos DB container.
        
        Args:
            query: SQL-like query string
            
        Returns:
            Query results as formatted string
        """
        return await self._call_mcp_tool("query_cosmos", {"query": query})

    async def list_containers(self) -> str:
        """List all available containers in the database."""
        return await self._call_mcp_tool("list_collections")

    async def describe_container(self, container_name: Optional[str] = None) -> str:
        """
        Describe the schema of a container.
        
        Args:
            container_name: Name of container to describe (optional)
            
        Returns:
            Schema description
        """
        args = {"container_name": container_name} if container_name else {}
        return await self._call_mcp_tool("describe_container", args)

    async def get_sample_documents(self, container_name: Optional[str] = None, limit: int = 5) -> str:
        """
        Get sample documents from a container.
        
        Args:
            container_name: Name of container (optional)
            limit: Number of documents to retrieve
            
        Returns:
            Sample documents as formatted string
        """
        args = {}
        if container_name:
            args["container_name"] = container_name
        if limit != 5:
            args["limit"] = limit
        return await self._call_mcp_tool("get_sample_documents", args)

    async def count_documents(self, container_name: Optional[str] = None) -> str:
        """
        Count documents in a container.
        
        Args:
            container_name: Name of container (optional)
            
        Returns:
            Document count
        """
        args = {"container_name": container_name} if container_name else {}
        return await self._call_mcp_tool("count_documents", args)

    async def get_partition_key_info(self, container_name: Optional[str] = None) -> str:
        """
        Get partition key information for a container.
        
        Args:
            container_name: Name of container (optional)
            
        Returns:
            Partition key information
        """
        args = {"container_name": container_name} if container_name else {}
        return await self._call_mcp_tool("get_partition_key_info", args)

    async def get_indexing_policy(self, container_name: Optional[str] = None) -> str:
        """
        Get indexing policy for a container.
        
        Args:
            container_name: Name of container (optional)
            
        Returns:
            Indexing policy as JSON string
        """
        args = {"container_name": container_name} if container_name else {}
        return await self._call_mcp_tool("get_indexing_policy", args)

    async def find_implied_links(self, container_name: Optional[str] = None) -> str:
        """
        Find implied relationships in a container.
        
        Args:
            container_name: Name of container (optional)
            
        Returns:
            Relationship analysis
        """
        args = {"container_name": container_name} if container_name else {}
        return await self._call_mcp_tool("find_implied_links", args)

    async def process_query(self, query: str) -> str:
        """
        Process a natural language query about Cosmos DB data.
        
        Args:
            query: Natural language query
            
        Returns:
            Response based on the query
        """
        try:
            logger.info(f"Processing Cosmos query: {query}")
            
            query_lower = query.lower()
            
            # Route queries to appropriate MCP tools based on intent
            if any(word in query_lower for word in ['list', 'show', 'containers', 'collections', 'databases']):
                if 'container' in query_lower or 'collection' in query_lower:
                    result = await self.list_containers()
                    return f"Available containers in the database:\n{result}"
                    
            elif any(word in query_lower for word in ['describe', 'schema', 'structure', 'fields']):
                # Extract container name if mentioned
                container_name = None
                if 'actions' in query_lower:
                    container_name = 'actions'
                elif 'container' in query_lower:
                    # Try to extract container name from query
                    words = query.split()
                    for i, word in enumerate(words):
                        if word.lower() == 'container' and i + 1 < len(words):
                            container_name = words[i + 1]
                            break
                
                result = await self.describe_container(container_name)
                return f"Container schema information:\n{result}"
                
            elif any(word in query_lower for word in ['sample', 'example', 'preview', 'show me']):
                # Extract container name and limit if mentioned
                container_name = None
                limit = 5
                
                if 'actions' in query_lower:
                    container_name = 'actions'
                    
                # Try to extract number
                import re
                numbers = re.findall(r'\d+', query)
                if numbers:
                    limit = min(int(numbers[0]), 10)  # Cap at 10 for safety
                
                result = await self.get_sample_documents(container_name, limit)
                return f"Sample documents:\n{result}"
                
            elif any(word in query_lower for word in ['count', 'how many', 'number of']):
                container_name = None
                if 'actions' in query_lower:
                    container_name = 'actions'
                    
                result = await self.count_documents(container_name)
                return f"Document count:\n{result}"
                
            elif any(word in query_lower for word in ['partition', 'partitioning', 'partition key']):
                container_name = None
                if 'actions' in query_lower:
                    container_name = 'actions'
                    
                result = await self.get_partition_key_info(container_name)
                return f"Partition key information:\n{result}"
                
            elif any(word in query_lower for word in ['index', 'indexing', 'policy']):
                container_name = None
                if 'actions' in query_lower:
                    container_name = 'actions'
                    
                result = await self.get_indexing_policy(container_name)
                return f"Indexing policy:\n{result}"
                
            elif any(word in query_lower for word in ['relationship', 'links', 'foreign key', 'references']):
                container_name = None
                if 'actions' in query_lower:
                    container_name = 'actions'
                    
                result = await self.find_implied_links(container_name)
                return f"Relationship analysis:\n{result}"
                
            elif 'select' in query_lower or 'from' in query_lower:
                # Direct SQL query
                result = await self.query_cosmos_db(query)
                return f"Query results:\n{result}"
                
            elif any(word in query_lower for word in ['time_agent', 'timeagent', 'time agent']):
                # Query for time_agent data specifically
                time_query = "SELECT * FROM c WHERE c.agent_name = 'TimeAgent' ORDER BY c._ts DESC"
                result = await self.query_cosmos_db(time_query)
                return f"Time Agent data:\n{result}"
                
            else:
                # Default: try to interpret as a general exploration request
                return await self._handle_general_query(query)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Sorry, I encountered an error while processing your query: {str(e)}"

    async def _handle_general_query(self, query: str) -> str:
        """Handle general queries by providing helpful information."""
        return f"""I can help you explore and query the Cosmos DB data using these capabilities:

🔍 **Query Operations:**
- Run SQL-like queries: "SELECT * FROM c WHERE c.agent_name = 'TimeAgent'"
- Find time_agent data: "Show me time_agent entries"

📋 **Data Exploration:**
- List containers: "Show me all containers"
- Describe schema: "Describe the actions container"
- Get samples: "Show me sample documents from actions"
- Count documents: "How many documents are in actions?"

🔧 **Technical Info:**
- Partition keys: "Show partition key info for actions"
- Indexing policies: "Show indexing policy"
- Relationships: "Find relationships in the data"

Your query: "{query}"

What would you like to explore? You can ask for any of the above operations or run direct SQL queries."""


# Export the class for backwards compatibility
CosmosQueryAgentWithMCP = CosmosQueryAgent
