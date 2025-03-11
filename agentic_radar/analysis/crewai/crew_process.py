import logging
from enum import Enum
from collections import defaultdict

class CrewProcessType(str, Enum):
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"

def infer_agent_connections(
    task_agent_mapping: dict[str, str],
    crew_task_mapping: dict[str, list[str]],
    crew_process_mapping: dict[str, CrewProcessType],
) -> tuple[dict[str, list[str]], list[str], list[str]]:
    """
    Infer connections between agents based on crew process types and task mappings.
    
    Args:
        task_agent_mapping: Mapping of tasks to their assigned agents
        crew_task_mapping: Mapping of crews to their lists of tasks
        crew_process_mapping: Mapping of crews to their process types
        
    Returns:
        Tuple containing:
        - Dictionary mapping source agents to lists of destination agents
        - List of start agents (first agents in sequential processes and all agents in hierarchical)
        - List of end agents (last agents in sequential processes and all agents in hierarchical)
    """
    agent_connections = defaultdict(list)
    start_agents = set()
    end_agents = set()
    
    for crew, tasks in crew_task_mapping.items():
        if crew not in crew_process_mapping:
            logging.warning(f"Crew {crew} missing in crew_process_mapping")
            continue
            
        process_type = crew_process_mapping[crew]
        
        if process_type == CrewProcessType.SEQUENTIAL:
            _handle_sequential_process(
                tasks, 
                task_agent_mapping, 
                agent_connections,
                start_agents,
                end_agents
            )
        elif process_type == CrewProcessType.HIERARCHICAL:
            _handle_hierarchical_process(
                tasks, 
                task_agent_mapping, 
                agent_connections,
                start_agents,
                end_agents
            )
        else:
            logging.warning(f"Unknown process type: {process_type}. Skipping crew {crew}...")
    
    return agent_connections, list(start_agents), list(end_agents)


def _handle_sequential_process(
    tasks: list[str],
    task_agent_mapping: dict[str, str],
    agent_connections: defaultdict[str, list[str]],
    start_agents: set,
    end_agents: set
) -> None:
    """
    Connect agents in the order their corresponding tasks are defined.
    
    In a sequential process:
    - The first agent is a start node
    - The last agent is an end node
    """
    valid_tasks = []
    valid_agents = []
    
    # First, identify all valid tasks and their agents
    for task in tasks:
        if task in task_agent_mapping:
            valid_tasks.append(task)
            valid_agents.append(task_agent_mapping[task])
        else:
            logging.warning(f"Task {task} is missing an agent assignment. Skipping...")
    
    if not valid_tasks:
        logging.warning("No valid tasks found for sequential process.")
        return
    
    # The first agent in a sequential process is a start agent
    if valid_agents:
        start_agents.add(valid_agents[0])
    
    # The last agent in a sequential process is an end agent
    if len(valid_agents) > 0:
        end_agents.add(valid_agents[-1])
    
    if len(valid_agents) == 1 and valid_agents[0] not in agent_connections:
        # Edge case: create agent even when it is the only agent in crew
        agent_connections[valid_agents[0]] = []

    # Create connections in sequence
    for i in range(len(valid_agents) - 1):
        src_agent = valid_agents[i]
        dest_agent = valid_agents[i + 1]
        agent_connections[src_agent].append(dest_agent)


def _handle_hierarchical_process(
    tasks: list[str],
    task_agent_mapping: dict[str, str],
    agent_connections: defaultdict[str, list[str]],
    start_agents: set,
    end_agents: set
) -> None:
    """
    Connect all agents with each other in a fully connected graph.
    
    In a hierarchical process:
    - All agents are both start and end nodes
    """
    valid_agents = []
    
    # Identify all valid agents
    for task in tasks:
        if task in task_agent_mapping:
            valid_agents.append(task_agent_mapping[task])
        else:
            logging.warning(f"Task {task} is missing an agent assignment. Skipping...")
    
    if len(valid_agents) < 2:
        logging.warning("Not enough valid agents for hierarchical process (need at least 2).")
        return
    
    # In hierarchical process, all agents are both start and end agents
    for agent in valid_agents:
        start_agents.add(agent)
        end_agents.add(agent)
    
    # Create a fully connected graph between all agents
    for i in range(len(valid_agents)):
        for j in range(len(valid_agents)):
            if i != j:  # Don't connect agent to itself
                src_agent = valid_agents[i]
                dest_agent = valid_agents[j]
                agent_connections[src_agent].append(dest_agent)