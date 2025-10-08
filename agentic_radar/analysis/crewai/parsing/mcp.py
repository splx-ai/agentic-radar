import ast
from typing import Union

from agentic_radar.analysis.ast_utils import parse_call
from agentic_radar.analysis.utils import walk_python_files

CREWAI_MCP_STDIO_SERVER_PARAMS_CTOR = "StdioServerParameters"


def collect_dicts_and_mcp_params(root_dir: str) -> dict[str, dict[str, str]]:
    """Parses all Python modules in the given directory and collects MCP server parameters.

    Args:
        root_dir (str): Path to the codebase directory
    Returns:
        dict[str, dict[str, str]]: Dictionary mapping variable name to corresponding MCP parameters (dict[str, str])
    """
    mcp_params: dict[str, dict[str, str]] = {}

    for file in walk_python_files(root_dir):
        with open(file, "r") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                print(f"Skipping file {file} due to syntax error.")
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and isinstance(
                        node.value, (ast.Dict, ast.Call)
                    ):
                        params = parse_mcp_params(node.value)
                        if params:
                            mcp_params[target.id] = params

    return mcp_params


def parse_mcp_params(node: Union[ast.Dict, ast.Call]) -> dict[str, str]:
    """Parse MCP server parameters from an AST node.

    Args:
        node (Union[ast.Dict, ast.Call]): AST node representing MCP server parameters
    Returns:
        dict[str, str]: Parsed MCP server parameters
    """
    params: dict[str, str] = {}
    if isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and isinstance(value, ast.Constant):
                params[key.value] = value.value
    else:
        parsed_call = parse_call(node)
        if parsed_call:
            function_name, args, kwargs = parsed_call
            if function_name == CREWAI_MCP_STDIO_SERVER_PARAMS_CTOR:
                for k, v in kwargs.items():
                    params[str(k)] = str(v)
    return params
