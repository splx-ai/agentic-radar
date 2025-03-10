import json
import logging
from importlib import resources

from agentic_radar.graph import ToolType

def categorize_tool(tool_name: str) -> ToolType:
    """
    Load the tool type from the JSON file and return a ToolType.
    """
    json_path = resources.files(__package__) / "tool_categories.json"
    try:
        with open(json_path, "r") as file:
            tool_mapping = json.load(file)

        category = tool_mapping.get(tool_name, "DEFAULT")
        return ToolType[category]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logging.error(f"Error loading tool categories: {e}")
        return ToolType.DEFAULT
