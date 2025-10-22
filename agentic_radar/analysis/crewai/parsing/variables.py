import ast
from typing import Dict

class VariableVisitor(ast.NodeVisitor):
    """
    A visitor to find all string variable assignments in a file.
    """
    def __init__(self):
        self.variables: Dict[str, str] = {}

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    self.variables[target.id] = node.value.value
                elif isinstance(node.value, ast.Str): # For older python versions
                    self.variables[target.id] = node.value.s
        self.generic_visit(node)

def find_variable_value(file_path: str, variable_name: str) -> str | None:
    """
    Parses a Python file to find the string value of a specific variable.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        
        # This visitor will find all top-level variable assignments
        class SingleVariableVisitor(ast.NodeVisitor):
            def __init__(self):
                self.value = None

            def visit_Assign(self, node: ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == variable_name:
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            self.value = node.value.value
                        elif isinstance(node.value, ast.Str):
                            self.value = node.value.s
                self.generic_visit(node)

        visitor = SingleVariableVisitor()
        visitor.visit(tree)
        return visitor.value
    except (FileNotFoundError, SyntaxError) as e:
        print(f"Warning: Could not parse variable '{variable_name}' from {file_path}. Error: {e}")
        return None
