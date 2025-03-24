from typing import Any, Optional

import yaml

from agentic_radar.analysis.crewai.models.tool import CrewAITool
from agentic_radar.analysis.crewai.tool_descriptions import (
    get_crewai_tools_descriptions,
)
from agentic_radar.analysis.utils import walk_yaml_files


def read_yaml_config_file(file_path) -> Any:
    with open(file_path, "r") as file:
        try:
            content = yaml.safe_load(file)
        except Exception as e:
            raise ValueError(f"Cannot parse YAML file: {file_path}. Error: {e}")

        return content


def is_agent_config(file_content: Any) -> bool:
    if not isinstance(file_content, dict):
        return False

    first_value = next(iter(file_content.values()))
    if (
        isinstance(first_value, dict)
        and "role" in first_value
        and "goal" in first_value
        and "backstory" in first_value
    ):
        return True

    return False


def is_task_config(file_content: Any) -> bool:
    if not isinstance(file_content, dict):
        return False

    first_value = next(iter(file_content.values()))
    if (
        isinstance(first_value, dict)
        and "description" in first_value
        and "expected_output" in first_value
    ):
        return True

    return False


def extract_agent_tools_from_config(
    file_content: dict[str, dict[str, Any]], crewai_tool_descriptions: dict[str, str]
) -> dict[str, list[CrewAITool]]:
    assert is_agent_config(file_content)

    yaml_agent_tool_mapping = {}

    for agent in file_content:
        tool_names: list[str] = file_content[agent].get("tools", [])
        tools: list[CrewAITool] = [
            CrewAITool(
                name=tool_name,
                custom=False,
                description=crewai_tool_descriptions.get(tool_name, ""),
            )
            for tool_name in tool_names
        ]
        yaml_agent_tool_mapping[agent] = tools

    return yaml_agent_tool_mapping


def extract_task_agent_from_config(
    file_content: dict[str, dict[str, Any]],
) -> dict[str, str]:
    assert is_task_config(file_content)

    yaml_task_agent_mapping = {}

    for task in file_content:
        agent: Optional[str] = file_content[task].get("agent", None)
        if not agent:
            continue
        yaml_task_agent_mapping[task] = agent

    return yaml_task_agent_mapping


def collect_agent_tools_from_config(
    root_dir: str,
) -> dict[str, dict[str, list[CrewAITool]]]:
    crewai_tools_descriptions = get_crewai_tools_descriptions()
    yaml_file_to_agent_tool_mapping: dict[str, dict[str, list[CrewAITool]]] = {}
    for file in walk_yaml_files(root_dir):
        try:
            file_content = read_yaml_config_file(file)
        except ValueError as e:
            print(f"Error while reading YAML file: {e}")
            continue
        if is_agent_config(file_content):
            yaml_agent_tool_mapping = extract_agent_tools_from_config(
                file_content, crewai_tools_descriptions
            )
            yaml_file_to_agent_tool_mapping[file] = yaml_agent_tool_mapping

    return yaml_file_to_agent_tool_mapping


def collect_task_agents_from_config(root_dir: str) -> dict[str, dict[str, str]]:
    yaml_file_to_task_agent_mapping: dict[str, dict[str, str]] = {}
    for file in walk_yaml_files(root_dir):
        try:
            file_content = read_yaml_config_file(file)
        except ValueError as e:
            print(f"Error while reading YAML file: {e}")
            continue
        if is_task_config(file_content):
            yaml_task_agent_mapping = extract_task_agent_from_config(file_content)
            yaml_file_to_task_agent_mapping[file] = yaml_task_agent_mapping

    return yaml_file_to_task_agent_mapping
