import ast
import json
import os
from importlib import resources
from typing import Dict, List, Set


def extract_imports_with_ast(file_content: str) -> List[str]:
    imports = []
    tree = ast.parse(file_content)

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
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                    imports = extract_imports_with_ast(file_content)
                    for single_import in imports:
                        all_imports.add(single_import)
            elif file.endswith(".ipynb"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    notebook = json.load(f)
                    file_content = ""
                    for cell in notebook["cells"]:
                        if cell["cell_type"] == "code":
                            for row in cell["source"]:
                                file_content += row
                    imports = extract_imports_with_ast(file_content)
                    for single_import in imports:
                        all_imports.add(single_import)

    return all_imports


def get_all_predefined_tools_from_directory(
    directory_path: str,
) -> List[Dict[str, Dict[str, str]]]:
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
