import json

import importlib_resources as resources

from agentic_radar.graph import ToolType


def categorize_tool(tool_name: str) -> ToolType:
    """
    Load the tool type from the JSON file and return a ToolType.
    """
    try:
        # Use resources.files().joinpath() to get the path, then use .read_text() to read the file
        json_text = (
            resources.files(__package__).joinpath("tool_categories.json").read_text()
        )
        tool_mapping = json.loads(json_text)
        category = tool_mapping.get(tool_name, "DEFAULT")
        return ToolType[category]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading tool categories: {e}")
        return ToolType.DEFAULT
