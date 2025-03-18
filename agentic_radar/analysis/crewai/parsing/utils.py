import ast
from typing import Optional, Sequence, Union, cast


def find_return_of_function_call(
    node: Union[ast.AST, Sequence[ast.AST]], function_name: str
) -> Optional[ast.Call]:
    """
    Recursively search for and return the function call node contained in an expression of the form 'return {function_name}()'.
    Args:
        node: An AST node or sequence of AST nodes to search within
        function_name: The name of the function to search for
    Returns:
        The function call node if found, otherwise None
    """
    # Handle list of statements
    if isinstance(node, (list, tuple)):
        for item in node:
            result = find_return_of_function_call(item, function_name)
            if result:
                return result
        return None

    # Check if this is a return statement
    if isinstance(node, ast.Return):
        if node.value and is_function_call(node.value, function_name):
            return cast(ast.Call, node.value)  # Return the function call node
        return None

    # For compound statements, check their bodies
    elif isinstance(node, ast.If):
        # Check the if body - body is a list of statements
        result = find_return_of_function_call(node.body, function_name)
        if result:
            return result
        # Check the else body if it exists
        if node.orelse:
            return find_return_of_function_call(node.orelse, function_name)
        return None
    elif isinstance(node, ast.IfExp):
        # For expression-based if statements
        if_result = find_return_of_function_call(node.body, function_name)
        if if_result:
            return if_result
        return find_return_of_function_call(node.orelse, function_name)
    elif (
        isinstance(node, ast.For)
        or isinstance(node, ast.While)
        or isinstance(node, ast.With)
    ):
        return find_return_of_function_call(node.body, function_name)
    elif isinstance(node, ast.Try):
        # Check try body
        result = find_return_of_function_call(node.body, function_name)
        if result:
            return result
        # Check except handlers
        if node.handlers:
            for handler in node.handlers:
                result = find_return_of_function_call(handler.body, function_name)
                if result:
                    return result
        # Check finally block
        if node.finalbody:
            return find_return_of_function_call(node.finalbody, function_name)
        return None

    return None


def is_function_call(node: ast.AST, function_name: str) -> bool:
    """
    Check if a node is a call to a function with the given name.

    Args:
        node: An AST node to check
        function_name: The name of the function to check for

    Returns:
        True if the node is a call to the function, otherwise False
    """
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == function_name:
            return True
        elif isinstance(node.func, ast.Attribute) and node.func.attr == function_name:
            return True
    return False
