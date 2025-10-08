import ast
from ast import NodeVisitor
from typing import Optional

from ...ast_utils import get_keyword_arg_value
from ...utils import walk_python_files
from ..models import MCPServerInfo, MCPServerType

MCP_SERVER_STDIO_FUNC_NAME = "MCPServerStdio"
MCP_SERVER_SSE_FUNC_NAME = "MCPServerSse"
MCP_SERVER_HTTP_FUNC_NAME = "MCPServerStreamableHttp"
HOSTED_MCP_SERVER_TOOL_FUNC_NAME = "HostedMCPTool"


def _mcp_server_type_from_func_name(func_name: str) -> Optional[MCPServerType]:
    if func_name == MCP_SERVER_STDIO_FUNC_NAME:
        return MCPServerType.STDIO
    elif func_name == MCP_SERVER_SSE_FUNC_NAME:
        return MCPServerType.SSE
    elif func_name == MCP_SERVER_HTTP_FUNC_NAME:
        return MCPServerType.HTTP
    elif func_name == HOSTED_MCP_SERVER_TOOL_FUNC_NAME:
        return MCPServerType.HOSTED
    else:
        return None


def _dictify(node: ast.Dict) -> dict[str, str]:
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
            parsed_dict[key.value] = " ".join(_listify(value))

    return parsed_dict


def _listify(node: ast.List) -> list[str]:
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


def _extract_hosted_mcp_tool(node: ast.Call) -> Optional[MCPServerInfo]:
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
        return None

    if node.func.id != HOSTED_MCP_SERVER_TOOL_FUNC_NAME:
        return None

    mcp_server_type = _mcp_server_type_from_func_name(node.func.id)
    if not mcp_server_type:
        return None

    for keyword in node.keywords:
        if not isinstance(keyword, ast.keyword) or not isinstance(keyword.arg, str):
            continue

    tool_config = get_keyword_arg_value(node, "tool_config")
    if not isinstance(tool_config, ast.Dict):
        print(
            f"Expected a dictionary for tool_config at line {node.lineno}, but got {type(tool_config).__name__}."
        )
        return None

    mcp_server_params = _dictify(tool_config)

    return MCPServerInfo(
        var="(unknown)",
        name=mcp_server_params.get("server_label", None),
        type=mcp_server_type,
        params=mcp_server_params,
    )


class MCPServerVisitor(NodeVisitor):
    def __init__(self):
        super().__init__()
        self.mcp_servers: dict[str, MCPServerInfo] = {}

    def visit_Assign(self, node):
        # Look for assignments like: mcp_server = MCPServerStdio(...) or mcp_server = MCPServerSse(...)
        if not isinstance(node.value, ast.Call) or not isinstance(
            node.value.func, ast.Name
        ):
            return

        mcp_server_type = _mcp_server_type_from_func_name(node.value.func.id)
        if not mcp_server_type:
            return

        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            print(
                f"Expected a single variable assignment for MCP server at line {node.lineno}, but got {len(node.targets)} targets."
            )
            return

        mcp_server_var = node.targets[0].id

        if mcp_server_type == MCPServerType.HOSTED:
            # Special handling for hosted MCP server tools
            hosted_mcp_info = _extract_hosted_mcp_tool(node.value)
            if hosted_mcp_info:
                hosted_mcp_info.var = mcp_server_var
                self.mcp_servers[mcp_server_var] = hosted_mcp_info
            return

        mcp_server_name = self._get_server_name(node.value)
        mcp_server_params = self._get_server_params(node.value)

        self.mcp_servers[mcp_server_var] = MCPServerInfo(
            var=mcp_server_var,
            name=mcp_server_name,
            type=mcp_server_type,
            params=mcp_server_params,
        )

    def _is_mcp_instance_from_with_item(self, with_item: ast.withitem) -> bool:
        return (
            isinstance(with_item.context_expr, ast.Call)
            and isinstance(with_item.context_expr.func, ast.Name)
            and with_item.context_expr.func.id
            in [
                MCP_SERVER_STDIO_FUNC_NAME,
                MCP_SERVER_SSE_FUNC_NAME,
                MCP_SERVER_HTTP_FUNC_NAME,
            ]
            and isinstance(with_item.optional_vars, ast.Name)
        )

    def _extract_mcp_instance(self, mcp_ctor: ast.Call, mcp_var: ast.Name) -> None:
        mcp_name = self._get_server_name(mcp_ctor)
        if not isinstance(mcp_ctor.func, ast.Name):
            return
        mcp_type = _mcp_server_type_from_func_name(mcp_ctor.func.id)
        if not mcp_type:
            return
        mcp_params = self._get_server_params(mcp_ctor)
        self.mcp_servers[mcp_var.id] = MCPServerInfo(
            var=mcp_var.id, name=mcp_name, type=mcp_type, params=mcp_params
        )

    def _is_mcp_reference_from_with_item(self, with_item: ast.withitem) -> bool:
        return (
            isinstance(with_item.context_expr, ast.Name)
            and isinstance(with_item.optional_vars, ast.Name)
            and with_item.context_expr.id in self.mcp_servers
        )

    def _extract_mcp_reference_from_with_item(
        self, mcp_ref: ast.Name, mcp_var: ast.Name
    ) -> None:
        if mcp_ref.id not in self.mcp_servers:
            print(
                f"Unknown MCP server reference '{mcp_ref.id}' at line {mcp_ref.lineno}."
            )
            return

        self.mcp_servers[mcp_var.id] = self.mcp_servers[mcp_ref.id]

    def visit_AsyncWith(self, node):
        for with_item in node.items:
            if self._is_mcp_instance_from_with_item(with_item):
                # Case 1, eg.: with MCPServerStdio(...) as mcp_server:
                self._extract_mcp_instance(
                    mcp_ctor=with_item.context_expr, mcp_var=with_item.optional_vars
                )
            elif self._is_mcp_reference_from_with_item(with_item):
                # Case 2, eg.: with filesystem_server as fs_srv:
                self._extract_mcp_reference_from_with_item(
                    mcp_ref=with_item.context_expr, mcp_var=with_item.optional_vars
                )

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

                params = _dictify(keyword.value)
                return params

        print(f"Expected a keyword argument 'params' at line {node.lineno}.")
        return {}

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
