from predefined_tools import get_all_predefined_tools_from_directory
from custom_tools import get_all_custom_tools_from_directory
from utils import build_global_registry
from graph import parse_all_graph_instances_in_directory
from models import NodeCategory, NodeType, Node, Edge

GRAPH_CLASS = "langgraph.graph.StateGraph"
ADD_CONDITIONAL_EDGES_METHOD_NAME = "add_conditional_edges"
ADD_NODE_METHOD_NAME = "add_node"

def analyze_graph_directory(root_directory):

    global_functions, global_variables = build_global_registry(root_directory)

    predefined_tools = get_all_predefined_tools_from_directory(root_directory)

    custom_tools = get_all_custom_tools_from_directory(root_directory)

    all_graphs = parse_all_graph_instances_in_directory(root_directory, GRAPH_CLASS, ADD_CONDITIONAL_EDGES_METHOD_NAME, ADD_NODE_METHOD_NAME, global_functions, global_variables)

    #for graph in all_graphs:
        #print(f"Graph: {graph["graph_name"]}")
        #print(graph["graph_info"], end="\n\n\n\n")

    ## This is an intermediate result until the part that connects nodes and tools is completed


    ## Example made for CLI integration, since all examples have one graph
    nodes = []
    edges = []

    for graph in all_graphs:
        for i, node in enumerate(graph["graph_info"]["nodes"]):
            type = ""
            if i%4 == 0:
                type = NodeType.TOOL
            elif i%5 == 0:
                type = NodeType.CUSTOM_TOOL
            elif i%6 == 0:
                type = NodeType.AGENT
            else:
                type = NodeType.BASIC

            nodes.append(Node(
                type = type,
                name = node["name"],
                label = node["name"]
            ))

        nodes.append(Node(
            type = NodeType.BASIC,
            name = "START",
            label = "START"
        ))

        nodes.append(Node(
            type = NodeType.BASIC,
            name = "END",
            label = "END"
        ))

        for basic_edge in graph["graph_info"]["basic_edges"]:
            edges.append(Edge(
                start_node = basic_edge["start_node"],
                end_node = basic_edge["end_node"]
            ))

        for conditional_edge in graph["graph_info"]["conditional_edges"]:
            edges.append(Edge(
                start_node = conditional_edge["start_node"],
                end_node = conditional_edge["end_node"],
                condition = "if else"
            ))

    return nodes, edges

if __name__ == "__main__":

    #analyze_graph_directory("./agentic_scanner/analysis/examples/Gladiator2")
    print(analyze_graph_directory("./agentic_scanner/analysis/examples/customer_service"))