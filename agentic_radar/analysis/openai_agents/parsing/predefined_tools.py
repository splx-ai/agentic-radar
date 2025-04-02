import json

import importlib_resources as resources

from ..models import Tool


def load_predefined_tools():
    predefined_tools = {}
    try:
        json_text = (
            resources.files(__package__).joinpath("predefined_tools.json").read_text()
        )
        tool_to_description = json.loads(json_text)
        if not isinstance(tool_to_description, dict):
            raise ValueError("predefined_tools.json must be a dictionary")

        for tool_name, description in tool_to_description.items():
            if not isinstance(tool_name, str) or not isinstance(description, str):
                raise ValueError(
                    f"Tool name and description must both be strings, got tool_name: {type(tool_name)} and description: {type(description)}"
                )

            predefined_tools[tool_name] = Tool(
                name=tool_name, custom=False, description=description
            )

        return predefined_tools

    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error loading predefined tools: {e}")
        return {}
