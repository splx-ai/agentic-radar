"""
This module contains the logic for parsing import statements in a Python file.
"""
import ast
import os
from typing import Dict, Tuple

class ImportVisitor(ast.NodeVisitor):
    """
    A visitor to extract import statements from a Python file's AST, including relative import levels.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.imports: Dict[str, str] = {}  # alias -> module_name
        # alias -> (module_name, original_name, level)
        self.used_imports: List[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        """
        Visits an Import node and adds the imported modules to the list of imports.
        """
        for alias in node.names:
            if alias.asname:
                self.imports[alias.asname] = alias.name
            else:
                self.imports[alias.name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Visits an ImportFrom node and adds the imported names to the list of imports.
        """
        module_path = self._resolve_module_path(node.module, node.level)
        if module_path:
            for alias in node.names:
                if alias.asname:
                    self.imports[alias.asname] = f"{module_path}.{alias.name}"
                else:
                    self.imports[alias.name] = f"{module_path}.{alias.name}"
        self.generic_visit(node)

    def _resolve_module_path(self, module_name: Optional[str], level: int) -> Optional[str]:
        """
        Resolves the absolute path of a module given its name and level.
        """
        if not module_name:
            return None

        if level == 0:
            return module_name

        base_path = os.path.dirname(self.file_path)
        for _ in range(level - 1):
            base_path = os.path.dirname(base_path)

        return ".".join(base_path.split(os.sep) + [module_name])

def get_imports(file_path: str) -> Tuple[Dict[str, str], List[str]]:
    """
    Parses a Python file and returns a dictionary of imports and a list of used imports.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    tree = ast.parse(content)
    visitor = ImportVisitor(file_path)
    visitor.visit(tree)
    return visitor.imports, visitor.used_imports
