"""
Module for generating visual representations of n8n workflow graphs.
"""
import json
from typing import Dict, Any
import os
import logging
import matplotlib.pyplot as plt
import networkx as nx
from ...graph import GraphDefinition

logger = logging.getLogger(__name__)

def generate_position_based_graph(workflow_json: Dict[str, Any], output_path: str = None) -> None:
    """
    Generate a graph visualization based on node positions in an n8n workflow.
    
    Args:
        workflow_json: The n8n workflow JSON data
        output_path: Optional path to save the generated graph image
    """
    # Create a directed graph
    G = nx.DiGraph()
    
    # Dictionary to track node name by ID for edge creation
    node_id_to_name = {}
    
    # Add nodes to the graph with their positions
    for node in workflow_json.get("nodes", []):
        node_id = node.get("id")
        node_name = node.get("name")
        position = node.get("position", [0, 0])
        
        # Store node ID to name mapping for edges
        node_id_to_name[node_id] = node_name
        
        # Add node to the graph
        G.add_node(node_name, pos=(position[0], position[1]))
    
    # Add edges to the graph
    for source_node, connections in workflow_json.get("connections", {}).items():
        for connection_type, connection_lists in connections.items():
            for connection_list in connection_lists:
                for connection in connection_list:
                    target_node_id = connection.get("node")
                    if target_node_id in node_id_to_name:
                        target_node = node_id_to_name[target_node_id]
                        G.add_edge(source_node, target_node)
    
    # Get node positions for drawing
    pos = nx.get_node_attributes(G, 'pos')
    
    # If no positions were found, use spring layout
    if not pos:
        logger.warning("No position data found in workflow, using spring layout")
        pos = nx.spring_layout(G)
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20, width=1.5)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    
    # Remove axis
    plt.axis('off')
    
    # Set title
    workflow_name = workflow_json.get("name", "n8n Workflow")
    plt.title(workflow_name, fontsize=15)
    
    # Save or show the graph
    if output_path:
        plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
        logger.info(f"Graph saved to {output_path}")
    else:
        plt.show()
    
    plt.close()

def generate_graph_from_graph_definition(graph_def: GraphDefinition, output_path: str = None) -> None:
    """
    Generate a graph visualization based on a GraphDefinition object.
    
    Args:
        graph_def: The GraphDefinition object
        output_path: Optional path to save the generated graph image
    """
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes to the graph with their positions
    for node in graph_def.nodes:
        # Add node to the graph
        if node.position_x is not None and node.position_y is not None:
            G.add_node(node.name, pos=(node.position_x, node.position_y))
        else:
            G.add_node(node.name)
    
    # Add edges to the graph
    for edge in graph_def.edges:
        G.add_edge(edge.start, edge.end)
    
    # Get node positions for drawing
    pos = nx.get_node_attributes(G, 'pos')
    
    # If no positions were found, use spring layout
    if not pos:
        logger.warning("No position data found in graph definition, using spring layout")
        pos = nx.spring_layout(G)
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20, width=1.5)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    
    # Remove axis
    plt.axis('off')
    
    # Set title
    plt.title(graph_def.name, fontsize=15)
    
    # Save or show the graph
    if output_path:
        plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
        logger.info(f"Graph saved to {output_path}")
    else:
        plt.show()
    
    plt.close()

def generate_graph_from_file(file_path: str, output_path: str = None) -> None:
    """
    Generate a graph visualization from an n8n workflow JSON file.
    
    Args:
        file_path: Path to the n8n workflow JSON file
        output_path: Optional path to save the generated graph image
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            workflow_json = json.load(f)
        
        generate_position_based_graph(workflow_json, output_path)
    except Exception as e:
        logger.error(f"Error generating graph from file {file_path}: {str(e)}")
