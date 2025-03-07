import json
import logging
from agentic_radar.graph import ToolType

def categorize_tool(tool_name: str, json_path: str = "./agentic_radar/analysis/crewai/tool_categories.json") -> ToolType:
    """
    Load the tool type from the JSON file and return a ToolType.
    """
    try:
        with open(json_path, "r") as file:
            tool_mapping = json.load(file)

        category = tool_mapping.get(tool_name, "DEFAULT")
        return ToolType[category]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logging.error(f"Error loading tool categories: {e}")
        return ToolType.DEFAULT

if __name__ == "__main__":
    print(categorize_tool("DirectoryReadTool"))