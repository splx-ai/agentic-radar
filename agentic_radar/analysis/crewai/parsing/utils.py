import ast
from typing import Optional

def find_return_of_function_call(node: ast.AST, function_name: str) -> Optional[ast.Call]:
    """
    Recursively search for and return the function call node contained in an expression of the form 'return {function_name}()'.
    
    Args:
        node: An AST node to search within
        
    Returns:
        The function call node if found, otherwise None
    """
    # Check if this is a return statement
    if isinstance(node, ast.Return):
        if is_function_call(node.value, function_name):
            return node.value  # Return the function call node
        return None
        
    # For compound statements, check their bodies
    elif isinstance(node, ast.If) or isinstance(node, ast.IfExp):
        # Check the if body
        result = find_return_of_function_call(node.body, function_name)
        if result:
            return result
            
        # Check the else body if it exists
        if hasattr(node, 'orelse') and node.orelse:
            return find_return_of_function_call(node.orelse, function_name)
        
        return None
        
    elif isinstance(node, ast.For) or isinstance(node, ast.While) or isinstance(node, ast.With):
        return find_return_of_function_call(node.body, function_name)
        
    elif isinstance(node, ast.Try):
        # Check try body
        result = find_return_of_function_call(node.body, function_name)
        if result:
            return result
            
        # Check except handlers
        if hasattr(node, 'handlers') and node.handlers:
            for handler in node.handlers:
                result = find_return_of_function_call(handler.body, function_name)
                if result:
                    return result
                    
        # Check finally block
        if hasattr(node, 'finalbody') and node.finalbody:
            return find_return_of_function_call(node.finalbody, function_name)
            
        return None
        
    # For collections of statements, check each one
    elif isinstance(node, list):
        for item in node:
            result = find_return_of_function_call(item, function_name)
            if result:
                return result
                
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