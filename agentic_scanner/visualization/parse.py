from typing import List, Optional

import pydot
from pydantic import BaseModel, Field

from agentic_scanner.visualization.edge import ConditionalEdge, Edge
from agentic_scanner.visualization.graph import Graph
from agentic_scanner.visualization.node import (
    AgentNode,
    BasicNode,
    CustomToolNode,
    NodeType,
    ToolNode,
    ToolType,
)


class NodeDefinition(BaseModel):
    node_type: NodeType = Field(alias="type")
    name: str
    label: Optional[str] = None
    category: Optional[ToolType] = None

    def to_pydot(self) -> pydot.Node:
        if self.node_type == NodeType.AGENT:
            return AgentNode(self.name, self.label or self.name)
        if self.node_type == NodeType.BASIC:
            return BasicNode(self.name, self.label or self.name)
        if self.node_type == NodeType.TOOL:
            return ToolNode(self.name, self.label or self.name, self.category)
        if self.node_type == NodeType.CUSTOM_TOOL:
            return CustomToolNode(self.name, self.label or self.name)
        raise ValueError(f"Unknown node type: {self.node_type}")


class EdgeDefinition(BaseModel):
    start: str
    end: str
    condition: Optional[str] = None

    def to_pydot(self) -> pydot.Edge:
        if self.condition is not None:
            return ConditionalEdge(self.start, self.end, self.condition)
        return Edge(self.start, self.end)


class GraphDefinition(BaseModel):
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]


def __from_input(definition: GraphDefinition) -> Graph:
    return Graph(
        nodes=[node.to_pydot() for node in definition.nodes],
        edges=[edge.to_pydot() for edge in definition.edges],
    )


def from_json(definition: str) -> Graph:
    return __from_input(GraphDefinition.model_validate_json(definition))


def from_dict(definition: dict) -> Graph:
    return __from_input(GraphDefinition.model_validate(definition))
