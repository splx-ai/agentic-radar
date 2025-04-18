import json
import os
import logging
from typing import List, Tuple, Dict

from ...analysis.analyze import Analyzer
from ...graph import GraphDefinition, EdgeDefinition, NodeDefinition, NodeType
from .converter import convert_connections, convert_nodes
from .models import N8nConnection, N8nNode
from .parsing import parse_n8n_connections, parse_n8n_nodes


class N8nAnalyzer(Analyzer):
    """
    Analyzer for n8n workflow configurations.
    
    This analyzer parses n8n workflow JSON files, extracts nodes and connections,
    and builds graph definitions representing the workflow structure.
    
    Attributes:
        connected_only (bool): If True, only include workflows with connections.
        langchain_only (bool): If True, only include workflows with LangChain nodes.
    """
    
    def __init__(self, connected_only=False, langchain_only=False):
        """
        Initialize the n8n analyzer.
        
        Args:
            connected_only (bool): If True, only include workflows with connections.
            langchain_only (bool): If True, only include workflows with LangChain nodes.
        """
        super().__init__()
        self.connected_only = connected_only
        self.langchain_only = langchain_only
        self.logger = logging.getLogger(__name__)

    def parse_n8n_config_file(
        self, file_path: str
    ) -> Tuple[List[N8nNode], List[N8nConnection], str]:
        """
        Parse an n8n workflow configuration file.
        
        Args:
            file_path (str): The path to the n8n workflow JSON file.
            
        Returns:
            Tuple containing:
                - List of N8nNode objects
                - List of N8nConnection objects
                - Workflow name as a string
        """
        n8n_nodes = []
        n8n_connections = []
        workflow_name = ""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    config = json.load(f)
                    if config.get("nodes", False) and config.get("connections", False):
                        n8n_nodes = parse_n8n_nodes(config.get("nodes"))
                        n8n_connections = parse_n8n_connections(config.get("connections"))
                        if config.get("name", False):
                            workflow_name = config.get("name")
                        else:
                            # Use splitext instead of strip for more reliable extension removal
                            workflow_name = os.path.splitext(os.path.basename(file_path))[0]
                except json.JSONDecodeError:
                    self.logger.error(f"Failed to parse JSON file: {file_path}")
        except IOError as e:
            self.logger.error(f"Error reading file {file_path}: {str(e)}")

        return n8n_nodes, n8n_connections, workflow_name

    def has_langchain_nodes(self, n8n_nodes: List[N8nNode]) -> bool:
        """
        Check if any of the nodes are LangChain nodes.
        
        Args:
            n8n_nodes (List[N8nNode]): The list of n8n nodes to check.
            
        Returns:
            bool: True if any node is a LangChain node, False otherwise.
        """
        return any("langchain" in node.type.lower() for node in n8n_nodes)

    def ensure_nodes_exist(self, nodes: List[NodeDefinition], edges: List[EdgeDefinition]) -> List[NodeDefinition]:
        """
        Ensure that all nodes referenced in edges exist in the nodes list.
        
        This method identifies nodes that are referenced in edges but missing from the nodes list,
        and adds them as basic nodes to ensure the graph remains connected.
        
        Args:
            nodes (List[NodeDefinition]): The list of existing node definitions.
            edges (List[EdgeDefinition]): The list of edge definitions.
            
        Returns:
            List[NodeDefinition]: Updated list of nodes with any missing nodes added.
        """
        existing_node_names = {node.name for node in nodes}
        missing_node_names = set()
        
        # Find nodes that are referenced in edges but don't exist in nodes list
        for edge in edges:
            if edge.start not in existing_node_names:
                missing_node_names.add(edge.start)
            if edge.end not in existing_node_names:
                missing_node_names.add(edge.end)
        
        # Add missing nodes to the nodes list
        if missing_node_names:
            self.logger.info(f"Adding {len(missing_node_names)} missing nodes to the graph: {', '.join(missing_node_names)}")
            for name in missing_node_names:
                nodes.append(
                    NodeDefinition(
                        type=NodeType.BASIC,
                        name=name,
                        label=name
                    )
                )
        
        return nodes

    def analyze(self, root_directory: str) -> List[GraphDefinition]:
        """
        Analyze n8n workflow files in the given directory and build graph definitions.
        
        Args:
            root_directory (str): The root directory to search for n8n workflow files.
            
        Returns:
            List[GraphDefinition]: A list of graph definitions representing n8n workflows.
        """
        workflow_graphs = []
        self.logger.info(f"Analyzing n8n workflows in {root_directory}")
        
        workflow_count = 0
        skipped_count = 0

        for root, _, files in os.walk(root_directory):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    n8n_nodes, n8n_connections, workflow_name = self.parse_n8n_config_file(file_path)

                    # Skip if we couldn't parse any nodes or connections
                    if not n8n_nodes:
                        self.logger.warning(f"No nodes found in workflow: {file_path}")
                        skipped_count += 1
                        continue
                        
                    # Skip workflows without connections if connected_only is True
                    if self.connected_only and not n8n_connections:
                        self.logger.info(f"Skipping workflow '{workflow_name}' as it has no connections")
                        skipped_count += 1
                        continue
                    
                    # Skip workflows without LangChain nodes if langchain_only is True
                    if self.langchain_only and not self.has_langchain_nodes(n8n_nodes):
                        self.logger.info(f"Skipping workflow '{workflow_name}' as it has no LangChain nodes")
                        skipped_count += 1
                        continue
                        
                    nodes, tools = convert_nodes(n8n_nodes)
                    edges = convert_connections(n8n_connections)
                    
                    # Ensure all nodes referenced in edges exist in the nodes list
                    nodes = self.ensure_nodes_exist(nodes, edges)
                    
                    workflow_graphs.append(GraphDefinition(
                        name=workflow_name, 
                        nodes=nodes, 
                        edges=edges, 
                        tools=tools
                    ))
                    workflow_count += 1
        
        self.logger.info(f"Analysis complete: {workflow_count} workflows processed, {skipped_count} workflows skipped")
        return workflow_graphs

        return workflow_graphs
