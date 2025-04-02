import json

import importlib_resources as resources

from agentic_radar.graph import ToolType


def load_tool_categories() -> dict[str, ToolType]:
    tool_to_category: dict[str, ToolType] = {}
    try:
        json_text = resources.files(__package__).joinpath("categories.json").read_text()
        tool_to_category_name = json.loads(json_text)
        if not isinstance(tool_to_category_name, dict):
            raise ValueError("categories.json must be a dictionary")

        for tool_name, category_name in tool_to_category_name.items():
            if not isinstance(tool_name, str) or not isinstance(category_name, str):
                raise ValueError(
                    f"Tool name and category must both be strings, got tool_name: {type(tool_name)} and category_name: {type(category_name)}"
                )
            if hasattr(ToolType, category_name):
                category = ToolType[category_name]
            else:
                print(
                    f"Warning: Unknown tool type {category_name} for tool {tool_name} while loading tool categories."
                )
                category = ToolType.DEFAULT
            tool_to_category[tool_name] = category

        return tool_to_category

    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error loading tool categories: {e}")
        return {}
