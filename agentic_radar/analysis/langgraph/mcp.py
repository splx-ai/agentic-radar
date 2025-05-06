import ast
import json
from typing import Dict, List

from agentic_radar.analysis.utils import walk_python_files_and_notebooks

STDIO_SERVER_PARAMS_CLASS = "mcp.StdioServerParameters"
MULTISERVER_MCP_CLIENT_CLASS = "langchain_mcp_adapters.client.MultiServerMCPClient"

class MCPServerInstanceTracker(ast.NodeVisitor):
    """
    A node visitor that finds instances of connections to MCP servers.
    """

    def __init__(
        self,
        stdio_server_params_fqcn: str,
        multiserver_mcp_client_fqcn: str
    ):
        self.stdio_server_params_fqcn = stdio_server_params_fqcn
        self.multiserver_mcp_client_fqcn = multiserver_mcp_client_fqcn

        self.import_aliases: Dict[str, str] = {}
        self.import_aliases_fully: Dict[str, str] = {}

        self.stdio_server_params_instances: List[dict] = []

        self.multiserver_mcp_client_instances: dict[str,dict] = {}

        self.mcp_client_vars: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        """
        Handle statements like:
          import examples
          import examples.graph as ex
        """
        for alias in node.names:
            local_name = alias.asname if alias.asname else alias.name
            self.import_aliases[local_name] = alias.name

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Handle statements like:
          from examples.graph import Graph
          from examples import graph as gph
        """

        if node.module is None:
            self.generic_visit(node)
            return

        base_module = node.module
        for alias in node.names:
            local_name = alias.asname if alias.asname else alias.name
            self.import_aliases_fully[local_name] = f"{base_module}.{alias.name}"

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        callee_fq = self._resolve_fq_name(node.func)

        if callee_fq == self.stdio_server_params_fqcn:
            self.stdio_server_params_instances.append({
                    kw.arg: ast.unparse(kw.value) for kw in node.keywords
                }
            )

        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id in self.mcp_client_vars:
                if node.func.attr == "connect_to_server":
                    if node.args:
                        arg0 = node.args[0]
                        if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                            server_name = arg0.value
                        else:
                            server_name = ast.unparse(arg0)
                    else:
                        server_name = "<missing_server_name>"

                    self.multiserver_mcp_client_instances[server_name] = {kw.arg: ast.unparse(kw.value) for kw in node.keywords}

        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                callee_fq = self._resolve_fq_name(item.context_expr.func)
                if callee_fq == self.multiserver_mcp_client_fqcn:
                    self._handle_multiserver_call(item.context_expr)

                    if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                        self.mcp_client_vars.add(item.optional_vars.id)
        self.generic_visit(node)

    def _handle_multiserver_call(self, call_node: ast.Call) -> None:
        callee_fq = self._resolve_fq_name(call_node.func)
        if callee_fq != self.multiserver_mcp_client_fqcn:
            return

        if not call_node.args:
            return

        config_dict = call_node.args[0]
        if not isinstance(config_dict, ast.Dict):
            return

        for key_node, value_node in zip(config_dict.keys, config_dict.values):
            if key_node is None:
                continue
            server_name = ast.literal_eval(key_node) if isinstance(key_node, ast.Constant) else ast.unparse(key_node)

            if isinstance(value_node, ast.Dict):
                config = {}
                for k, v in zip(value_node.keys, value_node.values):
                    if k is None:
                        continue
                    key_str = ast.literal_eval(k) if isinstance(k, ast.Constant) else ast.unparse(k)
                    val_str = ast.unparse(v)
                    config[key_str] = val_str
            else:
                config = {"<raw>": ast.unparse(value_node)}

            self.multiserver_mcp_client_instances[server_name] = config

    def _resolve_fq_name(self, node) -> str:
        """
        Attempt to resolve a node to a fully qualified name
        """
        if isinstance(node, ast.Name):
            if node.id in self.import_aliases_fully:
                return self.import_aliases_fully[node.id]
            return self.import_aliases.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            base_fq = self._resolve_fq_name(node.value)
            if base_fq:
                return base_fq + "." + node.attr
            return node.attr
        return ""

def get_all_mcp_servers_from_directory(
    directory_path: str,
) -> Dict[str, str]:

    all_mcp_servers = {}

    for file_path in walk_python_files_and_notebooks(directory_path):
        mcp_tracker = MCPServerInstanceTracker(
            STDIO_SERVER_PARAMS_CLASS,
            MULTISERVER_MCP_CLIENT_CLASS)
        if file_path.endswith(".py"):
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
                
                tree = ast.parse(file_content)
                mcp_tracker.visit(tree)

        elif file_path.endswith(".ipynb"):
            with open(file_path, "r", encoding="utf-8") as f:
                notebook = json.load(f)
                file_content = ""
                for cell in notebook["cells"]:
                    if cell["cell_type"] == "code":
                        for row in cell["source"]:
                            file_content += row

                tree = ast.parse(file_content)
                mcp_tracker.visit(tree)

        for i, stdio_server_params in enumerate(mcp_tracker.stdio_server_params_instances):
            all_mcp_servers[f"Unnamed Server {i+1}"] = str(stdio_server_params)

        for server_name, server_parameters in mcp_tracker.multiserver_mcp_client_instances.items():
            all_mcp_servers[server_name] = str(server_parameters)


    return all_mcp_servers