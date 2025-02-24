from typing import List

import pydot
from pydantic import BaseModel

from agentic_scanner import graph
from agentic_scanner.visualization.edge import ConditionalEdge, Edge
from agentic_scanner.visualization.graph import Graph
from agentic_scanner.visualization.node import (
    AgentNode,
    BasicNode,
    CustomToolNode,
    ToolNode,
)


class NodeDefinition(graph.NodeDefinition):
    def to_pydot(self) -> pydot.Node:
        if self.node_type == graph.NodeType.AGENT:
            return AgentNode(self.name, self.label or self.name)
        if self.node_type == graph.NodeType.BASIC:
            return BasicNode(self.name, self.label or self.name)
        if self.node_type == graph.NodeType.TOOL:
            return ToolNode(self.name, self.label or self.name, self.category)
        if self.node_type == graph.NodeType.CUSTOM_TOOL:
            return CustomToolNode(self.name, self.label or self.name)
        raise ValueError(f"Unknown node type: {self.node_type}")


class EdgeDefinition(graph.EdgeDefinition):
    def to_pydot(self) -> pydot.Edge:
        if self.condition is not None:
            return ConditionalEdge(self.start, self.end, self.condition)
        return Edge(self.start, self.end)


class GraphDefinition(BaseModel):
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]


def from_definition(definition: GraphDefinition) -> Graph:
    g = Graph(
        nodes=[node.to_pydot() for node in definition.nodes],
        edges=[edge.to_pydot() for edge in definition.edges],
    )
    print(g)
    return g


def from_json(definition: str) -> Graph:
    return from_definition(GraphDefinition.model_validate_json(definition))


def from_dict(definition: dict) -> Graph:
    return from_definition(GraphDefinition.model_validate(definition))
