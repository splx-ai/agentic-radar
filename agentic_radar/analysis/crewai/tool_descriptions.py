import ast
import importlib.util
import os
import re
from typing import Optional


def is_package_installed(package_name: str) -> bool:
    """
    Check if a package is installed in the current environment.

    Args:
        package_name: Name of the package to check

    Returns:
        True if the package is installed, False otherwise
    """
    spec = importlib.util.find_spec(package_name)
    return spec is not None


def parse_init_imports(init_path: str) -> list[tuple[str, str]]:
    """
    Parse the import statements from __init__.py to extract tool classes and their module paths.

    Args:
        init_path: Path to the __init__.py file

    Returns:
        List of tuples containing (class_name, module_path)
    """
    try:
        with open(init_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Parse the file
        parsed_ast = ast.parse(content)

        imports = []

        # Look for import statements
        for node in parsed_ast.body:
            if isinstance(node, ast.ImportFrom):
                # Get the module path (e.g., '.ai_mind_tool.ai_mind_tool')
                module_path = node.module

                if not module_path:
                    continue

                # Get the imports (e.g., 'AIMindTool')
                for name in node.names:
                    imports.append((name.name, module_path))

        return imports

    except Exception as e:
        print(f"Error parsing imports from {init_path}: {e}")
        return []


def find_tool_directory(tools_dir: str, module_path: str) -> Optional[str]:
    """
    Find the directory containing the tool based on its module path.

    Args:
        tools_dir: Base directory of all tools
        module_path: Relative module path (e.g., '.ai_mind_tool.ai_mind_tool')

    Returns:
        Path to the tool directory if found, None otherwise
    """
    # Remove leading dot if present
    if module_path.startswith("."):
        module_path = module_path[1:]

    # Split module path into parts
    parts = module_path.split(".")

    # Try to find the tool directory
    if len(parts) >= 1:
        # Try direct match (most tools have their own directory)
        tool_dir = os.path.join(tools_dir, parts[0])
        if os.path.isdir(tool_dir):
            return tool_dir

    return None


def extract_readme_content(readme_path: str) -> Optional[str]:
    """
    Extract content from a README.md file.

    Args:
        readme_path: Path to the README.md file

    Returns:
        Content of the README.md file if found, None otherwise
    """
    try:
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as file:
                return file.read()
        return None
    except Exception as e:
        print(f"Error reading README file at {readme_path}: {e}")
        return None


def extract_description_from_readme(readme_content: str) -> Optional[str]:
    """
    Extract the description section from a README.md file.

    Args:
        readme_content: Content of the README.md file

    Returns:
        Description section if found, None otherwise
    """
    if not readme_content:
        return None

    # Try to find description section
    description_match = re.search(
        r"## Description\s+(.*?)(?=##|\Z)", readme_content, re.DOTALL
    )
    if description_match:
        return description_match.group(1).strip()

    # If no description section found, try to use the content after the title
    title_match = re.search(r"# (.*?)\s+(.*?)(?=##|\Z)", readme_content, re.DOTALL)
    if title_match:
        return title_match.group(2).strip()

    # If still nothing found, return first paragraph
    first_para_match = re.search(r"^(.*?)(?=\n\n|\Z)", readme_content, re.DOTALL)
    if first_para_match:
        return first_para_match.group(1).strip()

    return None


def get_crewai_tools_descriptions() -> dict[str, str]:
    """
    Extract tool descriptions from README.md files in the tool directories.

    Returns:
        Dictionary mapping tool names to their descriptions
    """
    # First check if crewai_tools is installed
    if not is_package_installed("crewai_tools"):
        print("crewai_tools is not installed in the current environment.")
        return {}

    # Find the package location
    spec = importlib.util.find_spec("crewai_tools")
    if not spec or not spec.submodule_search_locations:
        return {}

    package_dir = spec.submodule_search_locations[0]
    tools_dir = os.path.join(package_dir, "tools")
    init_file = os.path.join(tools_dir, "__init__.py")

    if not os.path.exists(init_file):
        print(f"__init__.py not found at {init_file}")
        return {}

    # Parse imports from __init__.py
    imports = parse_init_imports(init_file)

    descriptions = {}

    for class_name, module_path in imports:
        # Find the tool directory
        tool_dir = find_tool_directory(tools_dir, module_path)

        if not tool_dir:
            descriptions[class_name] = f"Tool directory not found for {module_path}"
            continue

        # Look for README.md in the tool directory
        readme_path = os.path.join(tool_dir, "README.md")
        readme_content = extract_readme_content(readme_path)

        if readme_content:
            description = extract_description_from_readme(readme_content)
            if description:
                descriptions[class_name] = description
            else:
                descriptions[class_name] = "No description found in README.md"
        else:
            # Try to find README.md by traversing subdirectories
            readme_found = False
            for root, _, files in os.walk(tool_dir):
                if "README.md" in files:
                    readme_path = os.path.join(root, "README.md")
                    readme_content = extract_readme_content(readme_path)
                    if readme_content:
                        description = extract_description_from_readme(readme_content)
                        if description:
                            descriptions[class_name] = description
                            readme_found = True
                            break

            if not readme_found:
                descriptions[class_name] = "README.md not found for this tool"

    return descriptions
