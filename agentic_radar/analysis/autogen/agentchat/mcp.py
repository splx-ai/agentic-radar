import ast
import json

from agentic_radar.analysis.ast_utils import (
    kwargize_params,
    parse_simple_function_call_assignment,
)

from .models import MCPServer

MCP_SERVER_TYPES = [
    "StdioServerParams",
    "SseServerParams",
    "StreamableHttpServerParams",
]
STDIO_SERVER_PARAM_NAMES = [
    "command",
    "args",
    "env",
    "cwd",
    "encoding",
    "encoding_error_handler",
    "type",
    "read_timeout_seconds",
]
SSE_SERVER_PARAM_NAMES = ["type", "url", "headers", "timeout", "sse_read_timeout"]
STREAMABLE_HTTP_SERVER_PARAM_NAMES = [
    "type",
    "url",
    "headers",
    "timeout",
    "sse_read_timeout",
    "terminate_on_close",
]
TOOL_ADAPTER_FACTORY_FUNCTION = "from_server_params"
TOOL_ADAPTER_FACTORY_FUNCTION_PARAM_NAMES = ["server_params", "tool_name"]
MCP_SERVER_TOOLS_FACTORY_FUNCTION = "mcp_server_tools"
MCP_SERVER_TOOLS_FACTORY_FUNCTION_PARAM_NAMES = ["server_params", "session"]


def find_server_params(trees: list[ast.AST]) -> dict[str, MCPServer]:
    servers: dict[str, MCPServer] = {}
    for tree in trees:
        for node in ast.walk(tree):
            simple_function_call_assignment = parse_simple_function_call_assignment(
                node
            )
            if not simple_function_call_assignment:
                continue

            if simple_function_call_assignment.function_name not in MCP_SERVER_TYPES:
                continue

            if simple_function_call_assignment.function_name == "StdioServerParams":
                param_names = STDIO_SERVER_PARAM_NAMES
            elif simple_function_call_assignment.function_name == "SseServerParams":
                param_names = SSE_SERVER_PARAM_NAMES
            else:
                param_names = STREAMABLE_HTTP_SERVER_PARAM_NAMES

            server_params = kwargize_params(
                simple_function_call_assignment.args,
                simple_function_call_assignment.kwargs,
                param_names,
            )

            # Remove None values for cleaner output
            server_params = {k: v for k, v in server_params.items() if v is not None}

            servers[simple_function_call_assignment.target] = MCPServer(
                name=simple_function_call_assignment.target,
                description=json.dumps(server_params, indent=2),
            )
    return servers


def find_single_mcp_tool_adapters(
    trees: list[ast.AST], mcp_servers: dict[str, MCPServer]
) -> dict[str, MCPServer]:
    """Finds assignments like:
        adapter = await StreamableHttpMcpToolAdapter.from_server_params(server_params, "translation_tool")

    Args:
        trees (list[ast.AST]): The abstract syntax trees to search.
        mcp_servers (dict[str, MCPServer]): The MCP server params to use for finding adapters.

    Returns:
        dict[str, MCPServer]: A dictionary mapping adapter names to their MCP server instances.
    """
    adapters: dict[str, MCPServer] = {}
    for tree in trees:
        for node in ast.walk(tree):
            simple_function_call_assignment = parse_simple_function_call_assignment(
                node
            )
            if not simple_function_call_assignment:
                continue

            if (
                simple_function_call_assignment.function_name
                != TOOL_ADAPTER_FACTORY_FUNCTION
            ):
                continue

            adapter_params = kwargize_params(
                simple_function_call_assignment.args,
                simple_function_call_assignment.kwargs,
                TOOL_ADAPTER_FACTORY_FUNCTION_PARAM_NAMES,
            )

            server_name = adapter_params.get("server_params")
            tool_name = adapter_params.get("tool_name")
            if server_name not in mcp_servers:
                continue
            if not isinstance(tool_name, str):
                tool_name = "unknown-tool"
            mcp_server = mcp_servers[server_name].model_copy()
            mcp_server.tools.add(tool_name)
            adapters[simple_function_call_assignment.target] = mcp_server
    return adapters


def find_listed_mcp_tool_adapters(
    trees: list[ast.AST], mcp_servers: dict[str, MCPServer]
) -> dict[str, MCPServer]:
    """Finds assignments like:
    tools = await mcp_server_tools(server_params)

    Returns a dictionary mapping variables which contain list of adapters to their MCP server instances.
    """
    vars_to_adapters: dict[str, MCPServer] = {}
    for tree in trees:
        for node in ast.walk(tree):
            simple_function_call_assignment = parse_simple_function_call_assignment(
                node
            )
            if not simple_function_call_assignment:
                continue

            if (
                simple_function_call_assignment.function_name
                != MCP_SERVER_TOOLS_FACTORY_FUNCTION
            ):
                continue

            adapter_params = kwargize_params(
                simple_function_call_assignment.args,
                simple_function_call_assignment.kwargs,
                MCP_SERVER_TOOLS_FACTORY_FUNCTION_PARAM_NAMES,
            )

            server_name = adapter_params.get("server_params")
            if server_name not in mcp_servers:
                continue
            mcp_server = mcp_servers[server_name].model_copy()
            vars_to_adapters[simple_function_call_assignment.target] = mcp_server

    return vars_to_adapters
