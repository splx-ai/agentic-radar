from pathlib import Path

from ...analysis.analyze import Analyzer
from ...graph import EdgeDefinition as Edge
from ...graph import GraphDefinition
from ...graph import NodeDefinition as Node
from ...graph import NodeType, ToolType
from .custom_tools import get_all_custom_tools_from_directory
from .graph import parse_all_graph_instances_in_directory
from .predefined_tools import get_all_predefined_tools_from_directory
from .utils import build_global_registry

GRAPH_CLASS = "langgraph.graph.StateGraph"
COMMAND_CLASS = "langgraph.types.Command"
ADD_CONDITIONAL_EDGES_METHOD_NAME = "add_conditional_edges"
ADD_NODE_METHOD_NAME = "add_node"


class LangGraphAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, root_directory: str) -> GraphDefinition:
        global_functions, global_variables = build_global_registry(root_directory)

        predefined_tools = get_all_predefined_tools_from_directory(root_directory)

        custom_tools = get_all_custom_tools_from_directory(root_directory)

        all_graphs = parse_all_graph_instances_in_directory(
            root_directory,
            GRAPH_CLASS,
            COMMAND_CLASS,
            ADD_CONDITIONAL_EDGES_METHOD_NAME,
            ADD_NODE_METHOD_NAME,
            global_functions,
            global_variables,
        )
        nodes = []
        edges = []

        for graph in all_graphs:
            for i, node in enumerate(graph["graph_info"]["nodes"]):

                nodes.append(
                    Node(type=NodeType.BASIC, name=node["name"], label=node["name"])
                )

            nodes.append(Node(type=NodeType.BASIC, name="START", label="START"))

            nodes.append(Node(type=NodeType.BASIC, name="END", label="END"))

            for basic_edge in graph["graph_info"]["basic_edges"]:
                edges.append(
                    Edge(start=basic_edge["start_node"], end=basic_edge["end_node"])
                )

            for conditional_edge in graph["graph_info"]["conditional_edges"]:
                edges.append(
                    Edge(
                        start=conditional_edge["start_node"],
                        end=conditional_edge["end_node"],
                        condition="if else",
                    )
                )

        tools = []

        for predefined_tool in predefined_tools:
            tools.append(
                Node(
                    name=predefined_tool["name"],
                    type=NodeType.TOOL,
                    category=predefined_tool["category"],
                    vulnerabilities=[],  # TODO Add vulnerability mapping
                )
            )

        for custom_tool in custom_tools:
            tools.append(
                Node(
                    name=custom_tool["name"],
                    description=custom_tool["description"],
                    type=NodeType.CUSTOM_TOOL,
                    category=ToolType.DEFAULT,
                    vulnerabilities=[],  # TODO Add vulnerability mapping
                )
            )

        return GraphDefinition(
            name=Path(root_directory).name, nodes=nodes, edges=edges, tools=tools
        )
