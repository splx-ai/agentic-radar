import ast
import importlib
import json
import re
from typing import Dict, List, Optional, Set

import importlib_resources as resources

from agentic_radar.analysis.utils import walk_python_files_and_notebooks


def extract_imports_with_ast(file_content: str, file_path: str) -> List[str]:
    imports: List[str] = []
    try:
        tree = ast.parse(file_content)
    except Exception as e:
        print(f"Cannot parse Python module: {file_path}. Error: {e}")
        return imports

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
    all_imports: Set[str] = set()
    for file_path in walk_python_files_and_notebooks(directory_path):
        if file_path.endswith(".py"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                imports = extract_imports_with_ast(file_content, file_path)
                all_imports.update(imports)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        elif file_path.endswith(".ipynb"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    notebook = json.load(f)
                file_content = ""
                for cell in notebook.get("cells", []):
                    if cell.get("cell_type") == "code":
                        for row in cell.get("source", []):
                            file_content += row
                imports = extract_imports_with_ast(file_content, file_path)
                all_imports.update(imports)
            except Exception as e:
                print(f"Error parsing notebook {file_path}: {e}")
    return all_imports


def get_all_predefined_tools_from_directory(directory_path: str) -> List[Dict[str, str]]:
    input_file = resources.files(__package__) / "predefined_tools.json"
    with input_file.open("r", encoding="utf-8") as f:
        predefined_tools = json.loads(f.read())

    all_imports = parse_all_imports_from_directory(directory_path)
    possible_predefined_tools: List[Dict[str, str]] = []

    for name, values in predefined_tools.items():
        if any(single_import in all_imports for single_import in values.get("import_list", [])):
            new_possible_tool: Dict[str, str] = {"name": name}
            for value_name, value_content in values.items():
                new_possible_tool[value_name] = value_content

            # Attach a best-effort description for predefined tools so reports don't show blanks
            description = _derive_tool_description(
                tool_name=name,
                category=values.get("category"),
                import_list=values.get("import_list", []),
                import_howto=values.get("imports", ""),
            )
            if description:
                new_possible_tool["description"] = description

            possible_predefined_tools.append(new_possible_tool)

    return possible_predefined_tools


def _derive_tool_description(
    tool_name: str,
    category: Optional[str],
    import_list: List[str],
    import_howto: str,
) -> Optional[str]:
    """
    Try to construct a concise, human-friendly description for a predefined tool.
    Priority:
    1) Import the referenced symbol(s) and take the first sentence of the docstring
    2) Heuristic description based on name/category
    3) Fallback using the import instructions
    """
    # 1) Try to import from import_list and extract a docstring
    for target in import_list:
        doc = _get_object_docstring(target)
        if doc:
            summary = _summarize_docstring(doc)
            if summary:
                return summary

    # 2) Heuristic description
    cat_readable = category.replace("_", " ") if category else "tool"
    name_lower = tool_name.lower()
    if "search" in name_lower:
        return f"Search the web using {tool_name}."
    if "email" in name_lower or "gmail" in name_lower:
        return f"Access and manage emails via {tool_name}."
    if "drive" in name_lower or "storage" in name_lower:
        return f"Load files and documents from {tool_name}."
    if any(k in name_lower for k in ["sql", "database", "db"]):
        return f"Interact with databases using {tool_name}."
    if "wolfram" in name_lower:
        return "Answer computational queries using Wolfram Alpha."
    if "arxiv" in name_lower:
        return "Search and retrieve academic papers from arXiv."
    if "slack" in name_lower:
        return "Integrate with Slack to read or post messages."
    if "github" in name_lower:
        return "Interact with GitHub data and repositories."
    if category:
        return f"Predefined {cat_readable} for {tool_name}."

    # 3) Fallback: reference the import instructions succinctly
    if import_howto:
        return f"Predefined tool {tool_name}. See docs/imports for usage."
    return None


def _get_object_docstring(target: str) -> Optional[str]:
    """Given a dotted path like 'pkg.mod.ClassName', import it and return __doc__ if present."""
    try:
        if not target or target.count(".") == 0:
            return None
        parts = target.split(".")
        module_path = ".".join(parts[:-1])
        attr_name = parts[-1]
        module = importlib.import_module(module_path)
        obj = getattr(module, attr_name, None)
        if obj is None:
            return None
        doc = getattr(obj, "__doc__", None)
        if isinstance(doc, str) and doc.strip():
            return doc
        return None
    except Exception:
        return None


def _summarize_docstring(doc: str) -> str:
    """Return a short single-line description based on the first sentence/line of the docstring."""
    text = doc.strip()
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if not first_line:
        return ""
    parts = re.split(r"\.(\s|$)", first_line, maxsplit=1)
    candidate = parts[0] if parts and len(parts) > 0 else first_line
    candidate = candidate.strip()
    if len(candidate) > 200:
        candidate = candidate[:197].rstrip() + "..."
    return candidate
import ast
import importlib
import json
import re
from typing import Dict, List, Optional, Set

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

            # Attach a best-effort description for predefined tools so reports don't show blanks
            description = _derive_tool_description(
                tool_name=name,
                category=values.get("category"),
                import_list=values.get("import_list", []),
                import_howto=values.get("imports", ""),
            )
            if description:
                new_possible_tool["description"] = description
            possible_predefined_tools.append(new_possible_tool)

    return possible_predefined_tools


def _derive_tool_description(
    tool_name: str,
    category: Optional[str],
    import_list: List[str],
    import_howto: str,
) -> Optional[str]:
    """
    Try to construct a concise, human-friendly description for a predefined tool.
    Priority:
    1) Import the referenced symbol(s) and take the first sentence of the docstring
    2) Heuristic description based on name/category
    3) Fallback using the import instructions
    """
    # 1) Try to import from import_list and extract a docstring
    for target in import_list:
        doc = _get_object_docstring(target)
        if doc:
            summary = _summarize_docstring(doc)
            if summary:
                return summary

    # 2) Heuristic description
    if category:
        cat_readable = category.replace("_", " ")
    else:
        cat_readable = "tool"

    name_lower = tool_name.lower()
    if "search" in name_lower:
        return f"Search the web using {tool_name}."
    if "email" in name_lower or "gmail" in name_lower:
        return f"Access and manage emails via {tool_name}."
    if "drive" in name_lower or "storage" in name_lower:
        return f"Load files and documents from {tool_name}."
    if "sql" in name_lower or "database" in name_lower or "db" in name_lower:
        return f"Interact with databases using {tool_name}."
    if "wolfram" in name_lower:
        return "Answer computational queries using Wolfram Alpha."
    if "arxiv" in name_lower:
        return "Search and retrieve academic papers from arXiv."
    if "slack" in name_lower:
        return "Integrate with Slack to read or post messages."
    if "github" in name_lower:
        return "Interact with GitHub data and repositories."
    if category:
        return f"Predefined {cat_readable} for {tool_name}."

    # 3) Fallback: reference the import instructions succinctly
    if import_howto:
        return f"Predefined tool {tool_name}. See docs/imports for usage."
    return None


def _get_object_docstring(target: str) -> Optional[str]:
    """Given a dotted path like 'pkg.mod.ClassName', import it and return __doc__ if present."""
    try:
        # Split target into module path and attribute
        if not target or target.count(".") == 0:
            return None
        parts = target.split(".")
        module_path = ".".join(parts[:-1])
        attr_name = parts[-1]
        module = importlib.import_module(module_path)
        obj = getattr(module, attr_name, None)
        if obj is None:
            return None
        doc = getattr(obj, "__doc__", None)
        if isinstance(doc, str) and doc.strip():
            return doc
        return None
    except Exception:
        # If import fails (package not installed, etc.), just skip
        return None


def _summarize_docstring(doc: str) -> str:
    """Return a short single-line description based on the first sentence/line of the docstring."""
    text = doc.strip()
    # Prefer the first non-empty line
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if not first_line:
        return ""

    # Try to capture the first sentence up to ~200 chars
    # Split on period followed by space or end-of-line
    m = re.split(r"\.(\s|$)", first_line, maxsplit=1)
    if m and len(m) > 0:
        candidate = m[0]
    else:
        candidate = first_line

    candidate = candidate.strip()
    # Ensure reasonable length
    if len(candidate) > 200:
        candidate = candidate[:197].rstrip() + "..."
    return candidate
