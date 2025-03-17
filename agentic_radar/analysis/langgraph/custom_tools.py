import ast
import os
from typing import Dict, List
import json


def extract_custom_tools_with_ast(
    file_content: str, file_path: str
) -> List[Dict[str, str]]:
    custom_tools = []
    tree = ast.parse(file_content)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            decorator_names = []
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    decorator_names.append(decorator.id)
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name):
                        decorator_names.append(decorator.func.id)
                    elif isinstance(decorator.func, ast.Attribute):
                        decorator_names.append(decorator.func.attr)

            if "tool" in decorator_names:
                custom_tools.append({"name": node.name, "filepath": file_path, "description": ast.get_docstring(node)})

    return custom_tools


def get_all_custom_tools_from_directory(directory_path: str) -> List[Dict[str, str]]:
    all_custom_tools = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                    custom_tools = extract_custom_tools_with_ast(
                        file_content, file_path
                    )
                    for single_custom_tool in custom_tools:
                        all_custom_tools.append(single_custom_tool)
            elif file.endswith(".ipynb"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    notebook = json.load(f)
                    file_content = ""
                    for cell in notebook["cells"]:
                        if cell["cell_type"] == "code":
                            for row in cell["source"]:
                                file_content += row
                    custom_tools = extract_custom_tools_with_ast(
                        file_content, file_path
                    )
                    for single_custom_tool in custom_tools:
                        all_custom_tools.append(single_custom_tool)

    return all_custom_tools
