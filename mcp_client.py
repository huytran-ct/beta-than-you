import asyncio
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, create_model, Field
from dotenv import load_dotenv
import os
import json
from contextlib import AsyncExitStack

from llama_index.core.tools import FunctionTool

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()  # load environment variables from .env
CONFLUENCE_TOKEN =  os.getenv("CONFLUENCE__TOKEN")

def convert_schema_to_pydantic_model(model_name: str, schema: Dict[str, Any]) -> BaseModel:
    """
    Convert a JSON Schema dictionary into a Pydantic BaseModel,
    preserving field descriptions.
    
    Args:
        model_name: Name for the dynamically created model.
        schema: JSON Schema dictionary (expects 'properties' and 'required').
        
    Returns:
        A Pydantic BaseModel class.
    """
    fields = {}
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    
    # Mapping JSON Schema types to Python types.
    type_mapping = {
        "string": str,
        "number": float,
        "integer": int,
        "boolean": bool,
        "object": dict,
        "array": list,
    }
    
    for field_name, field_schema in properties.items():
        json_type = field_schema.get("type", "string")
        if isinstance(json_type, list):
            # If the type is a list, take the first element as the type.
            json_type = json_type[0]
        python_type = type_mapping.get(json_type, str)
        description = field_schema.get("description", "")
        default_value = field_schema.get("default", None)
        
        # If the field is required, use Ellipsis to indicate no default value,
        # and wrap it in Field with the description.
        if field_name in required_fields:
            field_info = Field(..., description=description)
        else:
            field_info = Field(default_value, description=description)
        
        fields[field_name] = (python_type, field_info)
    
    # Dynamically create a Pydantic model with the given fields.
    model = create_model(model_name, **fields)
    return model

class MCPClient:
    def __init__(self, config: Dict[str, Any]):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.config = config

    def _convert_to_llamaindex_tools(self, tools: List) -> List[FunctionTool]:
        """
        Convert a list of MCP tools (each with attributes: name, description, inputSchema)
        into a list of LlamaIndex FunctionTool objects.
        """
        llama_tools = []

        def make_async_tool_fn(t):
            async def async_tool_fn(**kwargs):
                print(f"Calling tool {t.name} with kwargs: {kwargs}")
                return await self.session.call_tool(t.name, kwargs.get('kwargs', {}))
            return async_tool_fn

        for tool in tools:
            async_fn = make_async_tool_fn(tool)

            # Optionally, create a synchronous wrapper if needed
            def sync_tool_fn(**kwargs):
                return asyncio.run(async_fn(**kwargs))
            # print(tool.inputSchema)
            llama_tool = FunctionTool.from_defaults(
                async_fn=async_fn,
                name=tool.name,
                description=tool.description,
                fn_schema=convert_schema_to_pydantic_model(f"{tool.name}Input", tool.inputSchema)
            )
            llama_tools.append(llama_tool)

        return llama_tools

    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command=self.config["command"],
            args=self.config["args"],
            env=self.config["env"]
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()


    async def get_server_tools(self):
        response = await self.session.list_tools()
        return response.tools
    
    async def get_llamaindex_server_tools(self):
        tools = await self.get_server_tools()
        print("\nConnected to server with tools:", [tool.name for tool in tools])

        return self._convert_to_llamaindex_tools(tools)

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
