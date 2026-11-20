import ast

from agentic_radar.analysis.langgraph.utils import get_source_from_file
from agentic_radar.analysis.utils import walk_python_files_and_notebooks


def find_agent_llm_variables(root_dir: str) -> set[str]:
    """
    Scan all .py files in root_dir for agent assignments.
    Detects two patterns:
    1. `llm_var = llm_var.bind_tools(...)` - traditional LangChain pattern
    2. `agent_var = create_react_agent(...)` - LangGraph prebuilt pattern (Issue #94)

    Returns a set of variable names that are LLM agents.
    """
    agent_vars = set()
    for filepath in walk_python_files_and_notebooks(root_dir):
        try:
            source = get_source_from_file(filepath)
            tree = ast.parse(source, filename=filepath)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                # Pattern 1: var = var.bind_tools(...)
                if (
                    isinstance(node.value.func, ast.Attribute)
                    and node.value.func.attr == "bind_tools"
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                ):
                    agent_vars.add(node.targets[0].id)

                # Pattern 2: var = create_react_agent(...) - Issue #94
                # Detects: agent_var = create_react_agent(llm, tools=[...])
                elif (
                    isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "create_react_agent"
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                ):
                    agent_vars.add(node.targets[0].id)

                # Pattern 2b: from langgraph.prebuilt import create_react_agent
                # Can also be accessed as module.create_react_agent
                elif (
                    isinstance(node.value.func, ast.Attribute)
                    and node.value.func.attr == "create_react_agent"
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                ):
                    agent_vars.add(node.targets[0].id)

    return agent_vars


def find_functions_calling_agent_invoke(
    root_dir: str, agent_vars: set[str]
) -> dict[str, bool]:
    """
    For each function in root_dir, determine if it calls .invoke on any agent variable.
    Returns a mapping: function_name -> True/False
    """
    result = {}
    for filepath in walk_python_files_and_notebooks(root_dir):
        try:
            source = get_source_from_file(filepath)
            tree = ast.parse(source, filename=filepath)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found = False
                for subnode in ast.walk(node):
                    if (
                        isinstance(subnode, ast.Call)
                        and isinstance(subnode.func, ast.Attribute)
                        and subnode.func.attr == "invoke"
                    ):
                        if isinstance(subnode.func.value, ast.Name):
                            if subnode.func.value.id in agent_vars:
                                found = True
                                break
                result[node.name] = found
    return result
