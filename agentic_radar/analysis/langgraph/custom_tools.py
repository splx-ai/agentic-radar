import ast
import json
from typing import Dict, List

from agentic_radar.analysis.utils import walk_python_files_and_notebooks


def extract_custom_tools_with_ast(
    file_content: str, file_path: str
) -> List[Dict[str, str]]:
    custom_tools = []

    try:
        tree = ast.parse(file_content)
    except Exception as e:
        print(f"Cannot parse Python module: {file_path}. Error: {e}")

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
                custom_tools.append(
                    {
                        "name": node.name,
                        "filepath": file_path,
                        "description": ast.get_docstring(node) or "",
                    }
                )

    return custom_tools


def get_all_custom_tools_from_directory(directory_path: str) -> List[Dict[str, str]]:
    all_custom_tools = []
    for file_path in walk_python_files_and_notebooks(directory_path):
        if file_path.endswith(".py"):
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
                custom_tools = extract_custom_tools_with_ast(file_content, file_path)
                for single_custom_tool in custom_tools:
                    all_custom_tools.append(single_custom_tool)
        elif file_path.endswith(".ipynb"):
            with open(file_path, "r", encoding="utf-8") as f:
                notebook = json.load(f)
                file_content = ""
                for cell in notebook["cells"]:
                    if cell["cell_type"] == "code":
                        for row in cell["source"]:
                            file_content += row
                custom_tools = extract_custom_tools_with_ast(file_content, file_path)
                for single_custom_tool in custom_tools:
                    all_custom_tools.append(single_custom_tool)

    return all_custom_tools
