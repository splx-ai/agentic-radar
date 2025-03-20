import ast
from typing import Optional, Union


def get_keyword_arg_value(call_node: ast.Call, keyword_name: str) -> Optional[ast.AST]:
    """
    Retrieves the value of a specific keyword argument from an ast.Call node.

    Args:
        call_node (ast.Call): The AST Call node to inspect.
        keyword_name (str): The name of the keyword argument to retrieve.

    Returns:
        Optional[ast.AST]: The AST node representing the value of the keyword argument,
                           or None if the keyword argument is not present.
    """
    if not isinstance(call_node, ast.Call):
        raise TypeError("Expected an ast.Call node")

    for keyword in call_node.keywords:
        if keyword.arg == keyword_name:
            return keyword.value

    return None

def is_simple_identifier(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        return True
    
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return True
    
    return False

def get_simple_identifier_name(node: Union[ast.Name, ast.Attribute]) -> str:
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return f"{node.value.id}.{node.attr}"
    else:
        raise TypeError(f"Node does not represent a simple identifier: {ast.dump(node)}")
        
