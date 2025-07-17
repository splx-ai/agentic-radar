from agentic_radar.graph import (
    Agent,
    EdgeDefinition,
    GraphDefinition,
    NodeDefinition,
    NodeType,
    ToolType,
)

from .models import Agent as AutogenAgent
from .models import Team, TeamType


def get_swarm_team_edges(team: Team) -> list[EdgeDefinition]:
    assert len(team.members) > 0, "Swarm team must have at least one member"

    edges = []
    all_agents = set(team.members)
    edges.append(
        EdgeDefinition(
            start="START",
            end=team.members[0].name,
        )
    )

    for agent in team.members:
        edges.append(
            EdgeDefinition(
                start=agent.name,
                end="END",
            )
        )
        for handoff in agent.handoffs:
            if handoff in all_agents:
                edges.append(
                    EdgeDefinition(start=agent.name, end=handoff, condition="handoff")
                )
    return edges


def get_round_robin_team_edges(team: Team) -> list[EdgeDefinition]:
    assert len(team.members) > 0, "Round Robin team must have at least one member"

    edges = []
    edges.append(
        EdgeDefinition(
            start="START",
            end=team.members[0].name,
        )
    )

    for i, agent in enumerate(team.members):
        next_agent = team.members[(i + 1) % len(team.members)]
        edges.append(
            EdgeDefinition(
                start=agent.name,
                end=next_agent.name,
            )
        )
        edges.append(EdgeDefinition(start=agent.name, end="END", condition="end"))
    return edges


def get_selector_team_edges(team: Team) -> list[EdgeDefinition]:
    assert len(team.members) > 0, "Selector team must have at least one member"

    edges = []
    edges.append(
        EdgeDefinition(
            start="START",
            end="Selector",
        )
    )

    for agent in team.members:
        edges.append(
            EdgeDefinition(
                start="Selector",
                end=agent.name,
            )
        )
        edges.append(EdgeDefinition(start=agent.name, end="END", condition="end"))
        edges.append(
            EdgeDefinition(
                start=agent.name,
                end="Selector",
            )
        )
    return edges


def _add_agent_node(
    agent: AutogenAgent,
    nodes: list[NodeDefinition],
    edges: list[EdgeDefinition],
    tools: list[NodeDefinition],
    agents: list[Agent],
) -> NodeDefinition:
    agent_node = NodeDefinition(
        name=agent.name,
        type=NodeType.AGENT,
        label=agent.name,
    )
    nodes.append(agent_node)

    if agent.tools:
        for tool in agent.tools:
            tool_node = NodeDefinition(
                name=tool.name,
                label=tool.name,
                description=tool.description,
                type=NodeType.CUSTOM_TOOL,
                category=ToolType.DEFAULT,
            )
            nodes.append(tool_node)
            edges.append(
                EdgeDefinition(start=agent.name, end=tool.name, condition="uses_tool")
            )
            tools.append(tool_node)

    agents.append(
        Agent(
            name=agent.name,
            llm=agent.llm,
            system_prompt=agent.system_prompt,
        )
    )

    return agent_node


def create_graph_definition(
    name: str, teams: list[Team], teamless_agents: list[AutogenAgent]
) -> GraphDefinition:
    nodes: list[NodeDefinition] = []
    edges: list[EdgeDefinition] = []
    agents: list[Agent] = []
    tools: list[NodeDefinition] = []

    start_node = NodeDefinition(
        name="START",
        type=NodeType.BASIC,
        label="START",
    )
    end_node = NodeDefinition(
        name="END",
        type=NodeType.BASIC,
        label="END",
    )
    nodes.append(start_node)
    nodes.append(end_node)

    for team in teams:
        if not team.members:
            continue

        for agent in team.members:
            _add_agent_node(agent, nodes, edges, tools, agents)

        if team.type == TeamType.SWARM:
            edges.extend(get_swarm_team_edges(team))
        elif team.type == TeamType.ROUND_ROBIN_GROUP_CHAT:
            edges.extend(get_round_robin_team_edges(team))
        elif (
            team.type == TeamType.SELECTOR_GROUP_CHAT
            or team.type == TeamType.MAGENTIC_ONE_GROUP_CHAT
        ):
            nodes.append(
                NodeDefinition(
                    name="Selector",
                    type=NodeType.AGENT,
                    label="Selector",
                )
            )
            edges.extend(get_selector_team_edges(team))
        else:
            raise ValueError(f"Unknown team type: {team.type}")

    for agent in teamless_agents:
        agent_node = _add_agent_node(agent, nodes, edges, tools, agents)
        edges.append(
            EdgeDefinition(
                start="START",
                end=agent_node.name,
            )
        )
        edges.append(
            EdgeDefinition(
                start=agent_node.name,
                end="END",
            )
        )

    graph_definition = GraphDefinition(
        name=name,
        nodes=nodes,
        edges=edges,
        agents=agents,
        tools=tools,
    )
    return graph_definition
