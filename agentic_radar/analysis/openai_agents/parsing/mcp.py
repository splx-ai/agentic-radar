import ast
from ast import NodeVisitor
from typing import Optional

from ...utils import walk_python_files
from ..models import MCPServerInfo, MCPServerType


class MCPServerVisitor(NodeVisitor):
    MCP_SERVER_STDIO = "MCPServerStdio"
    MCP_SERVER_SSE = "MCPServerSse"

    def __init__(self):
        super().__init__()
        self.mcp_servers: dict[str, MCPServerInfo] = {}

    def visit_AsyncWith(self, node):
        if not self._is_mcp_server(node):
            return

        mcp_server_call = node.items[0].context_expr

        assert isinstance(mcp_server_call, ast.Call) and isinstance(
            mcp_server_call.func, ast.Name
        )

        mcp_server_var = self._get_server_var(node)
        mcp_server_name = self._get_server_name(mcp_server_call)
        mcp_server_type = (
            MCPServerType.STDIO
            if mcp_server_call.func.id == self.MCP_SERVER_STDIO
            else MCPServerType.SSE
        )
        mcp_server_params = self._get_server_params(mcp_server_call)

        if mcp_server_var is None:
            print(
                f"Missing variable assignment for MCP server definition at line {node.lineno}."
            )
            return

        self.mcp_servers[mcp_server_var] = MCPServerInfo(
            var=mcp_server_var,
            name=mcp_server_name,
            type=mcp_server_type,
            params=mcp_server_params,
        )

    def _is_mcp_server(self, node: ast.AsyncWith) -> bool:
        if not isinstance(node, ast.AsyncWith):
            return False

        if len(node.items) != 1:
            return False

        mcp_server_call = node.items[0].context_expr

        if isinstance(mcp_server_call, ast.Call) and isinstance(
            mcp_server_call.func, ast.Name
        ):
            return (
                mcp_server_call.func.id == self.MCP_SERVER_STDIO
                or mcp_server_call.func.id == self.MCP_SERVER_SSE
            )
        return False

    def _get_server_params(self, node: ast.Call) -> dict[str, str]:
        for keyword in node.keywords:
            if (
                isinstance(keyword, ast.keyword)
                and isinstance(keyword.arg, str)
                and keyword.arg == "params"
            ):
                if not isinstance(keyword.value, ast.Dict):
                    print(
                        f"Expected a dictionary for params at line {keyword.lineno}, but got {type(keyword.value).__name__}."
                    )
                    return {}

                params = self._parse_dict_node(keyword.value)
                return params

        print(f"Expected a keyword argument 'params' at line {node.lineno}.")
        return {}

    def _parse_dict_node(self, node: ast.Dict) -> dict[str, str]:
        parsed_dict: dict[str, str] = {}
        for key, value in zip(node.keys, node.values):
            if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                if key:
                    print(
                        f"Expected a string key at line {key.lineno}, but got {type(key).__name__}."
                    )
                continue

            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parsed_dict[key.value] = value.value
            elif isinstance(value, ast.List):
                parsed_dict[key.value] = " ".join(self._parse_list_node(value))

        return parsed_dict

    def _parse_list_node(self, node: ast.List) -> list[str]:
        parsed_list = []
        for element in node.elts:
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                parsed_list.append(element.value)
            elif isinstance(element, ast.Name):
                parsed_list.append("{" + element.id + "}")
            else:
                print(
                    f"Expected a string element or variable at line {element.lineno}, but got {type(element).__name__}."
                )
        return parsed_list

    def _get_server_name(self, node: ast.Call) -> Optional[str]:
        for keyword in node.keywords:
            if (
                isinstance(keyword, ast.keyword)
                and isinstance(keyword.arg, str)
                and keyword.arg == "name"
            ):
                if isinstance(keyword.value, ast.Constant) and isinstance(
                    keyword.value.value, str
                ):
                    return keyword.value.value
                else:
                    print(
                        f"Expected a string value for 'name' at line {keyword.lineno}, but got {type(keyword.value).__name__}."
                    )
                    return None

        return None

    def _get_server_var(self, node: ast.AsyncWith) -> Optional[str]:
        if len(node.items) != 1:
            return None

        item = node.items[0]
        if isinstance(item.optional_vars, ast.Name):
            return item.optional_vars.id
        else:
            print(
                f"Expected variable for MCP server definition at line {node.lineno}, but got {type(item.optional_vars).__name__}."
            )
            return None


def collect_mcp_servers(root_dir: str) -> dict[str, MCPServerInfo]:
    all_mcp_servers: dict[str, MCPServerInfo] = {}
    for filename in walk_python_files(root_dir):
        with open(filename, "r") as file:
            try:
                file_content = ast.parse(file.read())
            except Exception as e:
                print(f"Cannot parse Python module: {file}. Error: {e}")
                continue
            visitor = MCPServerVisitor()
            visitor.visit(file_content)
            all_mcp_servers.update(visitor.mcp_servers)

    return all_mcp_servers
