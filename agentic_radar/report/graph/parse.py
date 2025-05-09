from typing import List

from pydantic import BaseModel, Field

from ... import graph
from .edge import ConditionalEdge, DefaultEdge, Edge
from .graph import Graph
from .node import AgentNode, BasicNode, CustomToolNode, MCPServerNode, Node, ToolNode


class NodeDefinition(graph.NodeDefinition):
    def parse(self) -> Node:
        if self.node_type == graph.NodeType.AGENT:
            return AgentNode(self.name, self.label or self.name)
        if self.node_type == graph.NodeType.BASIC:
            return BasicNode(self.name, self.label or self.name)
        if self.node_type == graph.NodeType.TOOL:
            return ToolNode(self.name, self.label or self.name, self.category)
        if self.node_type == graph.NodeType.CUSTOM_TOOL:
            return CustomToolNode(self.name, self.label or self.name)
        if self.node_type == graph.NodeType.MCP_SERVER:
            return MCPServerNode(self.name, self.label or self.name)
        raise ValueError(f"Unknown node type: {self.node_type}")


class EdgeDefinition(graph.EdgeDefinition):
    def parse(self) -> Edge:
        if self.condition is not None:
            return ConditionalEdge(self.start, self.end, self.condition)
        return DefaultEdge(self.start, self.end)


class GraphDefinition(BaseModel):
    name: str
    framework: str

    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]

    agents: List[graph.Agent] = Field(default_factory=list)
    tools: List[NodeDefinition] = Field(default_factory=list)
    hardened_prompts: dict[str, str] = Field(default_factory=dict)


def from_definition(definition: GraphDefinition) -> Graph:
    g = Graph(
        nodes=[node.parse() for node in definition.nodes],
        edges=[edge.parse() for edge in definition.edges],
    )
    return g


def from_json(definition: str) -> Graph:
    return from_definition(GraphDefinition.model_validate_json(definition))


def from_dict(definition: dict) -> Graph:
    return from_definition(GraphDefinition.model_validate(definition))
