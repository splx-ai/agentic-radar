import logging
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .tool import CrewAITool

class CrewAINodeType(str, Enum):
    AGENT = "Agent"
    TOOL = "Tool"
    CUSTOM_TOOL = "CustomTool"
    BASIC = "Basic"


class CrewAINode(BaseModel):
    name: str = Field(..., description="Name of the node")
    type: CrewAINodeType = Field(..., description="Type of the node")
    description: Optional[str] = Field(default=None, description="Short description of the node, used mainly for tool descriptions")

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
    nodes: set[CrewAINode] = Field(
        default_factory=set, description="List of nodes in the graph"
    )
    edges: set[CrewAIEdge] = Field(
        default_factory=set, description="List of edges in the graph"
    )

    def create_agents(self, agents: set[str]):
        for agent in agents:
            self.nodes.add(
                CrewAINode(name=agent, type=CrewAINodeType.AGENT)
            )

    def create_tools(self, tools: list[CrewAITool]):
        for tool in tools:
            tool_name = tool.name
            tool_type = CrewAINodeType.CUSTOM_TOOL if tool.custom else CrewAINodeType.TOOL
            description = tool.description
            self.nodes.add(CrewAINode(name=tool_name, type=tool_type, description=description))


    def connect_agent_to_tools(self, agent: str, tools: list[CrewAITool]):
        if not self.is_agent_in_graph(agent):
            return

        for tool in tools:
            tool_name = tool.name
            self.edges.add(
                CrewAIEdge(start_node=agent, end_node=tool_name, condition="tool_call")
            )
            self.edges.add(CrewAIEdge(start_node=tool_name, end_node=agent))
    
    def connect_agents(self, agent_connections: dict[str, list[str]]):
        for src_agent, dest_agents in agent_connections.items():
            if not self.is_agent_in_graph(src_agent):
                logging.warning(f"Source agent node {src_agent} is missing in graph, cannot create an edge with it...")
                continue

            condition = "hierarchical_delegation" if len(dest_agents) > 1 else None
            for dest_agent in dest_agents:
                if not self.is_agent_in_graph(src_agent):
                    logging.warning(f"Destination agent node {dest_agent} is missing in graph, cannot create an edge with it...")
                    continue
                self.edges.add(
                    CrewAIEdge(start_node=src_agent, end_node=dest_agent, condition=condition)
                )

    def add_start_end_nodes(self, start_agents: list[str], end_agents: list[str]):
        self.nodes.add(
            CrewAINode(name="START", type=CrewAINodeType.BASIC)
        )
        self.nodes.add(
            CrewAINode(name="END", type=CrewAINodeType.BASIC)
        )
        for start_agent in start_agents:
            condition = "start" if len(start_agents) > 1 else None
            self.edges.add(
                CrewAIEdge(start_node="START", end_node=start_agent, condition=condition)
            )
        for end_agent in end_agents:
            condition = "end" if len(start_agents) > 1 else None
            self.edges.add(
                CrewAIEdge(start_node=end_agent, end_node="END", condition=condition)
            )

    def is_agent_in_graph(self, agent: str):
        return CrewAINode(name=agent, type=CrewAINodeType.AGENT) in self.nodes
