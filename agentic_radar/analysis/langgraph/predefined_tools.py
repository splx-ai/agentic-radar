import ast
import json
from typing import Dict, List, Set

import importlib_resources as resources

from agentic_radar.analysis.utils import walk_python_files_and_notebooks


def extract_imports_with_ast(file_content: str, file_path: str) -> List[str]:
    imports = []

    try:
        tree = ast.parse(file_content)
    except Exception as e:
        print(f"Cannot parse Python module: {file_path}. Error: {e}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                full_import = alias.name
                imports.append(full_import)

        elif isinstance(node, ast.ImportFrom):
            module = node.module
            for alias in node.names:
                full_import = f"{module}.{alias.name}"
                imports.append(full_import)

    return imports


def parse_all_imports_from_directory(directory_path: str) -> Set[str]:
    all_imports = set()
    for file_path in walk_python_files_and_notebooks(directory_path):
        if file_path.endswith(".py"):
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
                imports = extract_imports_with_ast(file_content, file_path)
                for single_import in imports:
                    all_imports.add(single_import)
        elif file_path.endswith(".ipynb"):
            with open(file_path, "r", encoding="utf-8") as f:
                notebook = json.load(f)
                file_content = ""
                for cell in notebook["cells"]:
                    if cell["cell_type"] == "code":
                        for row in cell["source"]:
                            file_content += row
                imports = extract_imports_with_ast(file_content, file_path)
                for single_import in imports:
                    all_imports.add(single_import)

    return all_imports


def get_all_predefined_tools_from_directory(
    directory_path: str,
) -> List[Dict[str, str]]:
    input_file = resources.files(__package__) / "predefined_tools.json"
    with input_file.open("r") as f:
        predefined_tools = json.loads(f.read())

    all_imports = parse_all_imports_from_directory(directory_path)

    possible_predefined_tools = []

    for name, values in predefined_tools.items():
        if any(single_import in all_imports for single_import in values["import_list"]):
            new_possible_tool = {"name": name}
            for value_name, value_content in values.items():
                new_possible_tool[value_name] = value_content
            possible_predefined_tools.append(new_possible_tool)

    return possible_predefined_tools
