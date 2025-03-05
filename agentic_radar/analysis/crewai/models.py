from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

class CrewAINodeType(str, Enum):
    AGENT = "Agent"
    TOOL = "Tool"
    CUSTOM_TOOL = "CustomTool"
    TASK = "Task"

class CrewAINode(BaseModel):
    name: str = Field(..., description="Name of the node")
    type: CrewAINodeType = Field(..., description="Type of the node")

    class Config:
        frozen = True  # Makes it hashable and immutable

class CrewAIEdge(BaseModel):
    start_node: str = Field(..., description="Name of the starting node")
    end_node: str = Field(..., description="Name of the end node")
    condition: Optional[str] = Field(
        default=None, description="Optional condition for the edge"
    )

    class Config:
        frozen = True  # Makes it hashable and immutable

class CrewAIGraph(BaseModel):
    name: str = Field(..., description="Name of the graph")
    nodes: set[CrewAINode] = Field(default_factory=set, description="List of nodes in the graph")
    edges: set[CrewAIEdge] = Field(default_factory=set, description="List of edges in the graph")

    def create_nodes_and_connect_with_many(self, src_node: str, src_node_type: CrewAINodeType, dest_nodes: list[str], dest_nodes_type: CrewAINodeType):
        """Create src_node and dest_nodes and connect them."""
        self.nodes.add(CrewAINode(name=src_node, type=src_node_type))

        for dest_node in dest_nodes:
            self.nodes.add(CrewAINode(name=dest_node, type=dest_nodes_type))
            self.edges.add(CrewAIEdge(start_node=src_node, end_node=dest_node))