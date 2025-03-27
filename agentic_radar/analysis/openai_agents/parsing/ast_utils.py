import ast
from typing import Optional, Union


def get_nth_arg_value(call_node: ast.Call, n: int) -> ast.AST:
    """
    Retrieves the value of a specific positional argument from an ast.Call node.

    Args:
    call_node (ast.Call): The AST Call node to inspect.
    n (int): The index of the positional argument to retrieve (0-based).

    Returns:
    Optional[ast.AST]: The AST node representing the value of the nth positional argument,
    or None if the argument is not present.

    Raises:
    TypeError: If the input is not an ast.Call node.
    ValueError: If the provided index is out of bounds.
    """
    if not isinstance(call_node, ast.Call):
        raise TypeError("Expected an ast.Call node")

    if n < 0:
        raise ValueError("Argument index must be non-negative")
    if n >= len(call_node.args):
        raise ValueError(
            f"Argument index out of bounds (got n={n}, args length is {len(call_node.args)})"
        )

    return call_node.args[n]


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


def get_simple_identifier_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return node.attr
    else:
        raise TypeError(
            f"Node does not represent a simple identifier: {ast.dump(node)}"
        )


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
        if (
            isinstance(node.func, ast.Subscript)
            and is_simple_identifier(node.func.value)
            and get_simple_identifier_name(node.func.value) == function_name
        ):
            # Handles subscriptable function cases like myfunc = func[type]()
            return True

        if isinstance(node.func, ast.Name) and node.func.id == function_name:
            return True
        elif isinstance(node.func, ast.Attribute) and node.func.attr == function_name:
            return True
    return False


def find_decorator_by_name(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef],
    decorator_name: str,
) -> Optional[ast.AST]:
    """
    Find a decorator node by its name.

    Args:
        node (Union[ast.FunctionDef, ast.ClassDef]): The node to search for decorators.
        decorator_name (str): The name of the decorator to find.

    Returns:
        Optional[ast.AST]: The decorator node if found, None otherwise.
    """
    for decorator in node.decorator_list:
        # Handle simple name decorators like @function_tool
        if isinstance(decorator, ast.Name) and decorator.id == decorator_name:
            return decorator

        # Handle attribute decorators like @something.function_tool
        if isinstance(decorator, ast.Attribute) and decorator.attr == decorator_name:
            return decorator

        # Handle call decorators like @function_tool()
        if isinstance(decorator, ast.Call) and (
            isinstance(decorator.func, ast.Name)
            and decorator.func.id == decorator_name
            or isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == decorator_name
        ):
            return decorator

    return None


def has_decorator(
    node: Union[ast.FunctionDef, ast.ClassDef], decorator_name: str
) -> bool:
    """
    Check if a node has a specific decorator.

    Args:
        node (Union[ast.FunctionDef, ast.ClassDef]): The node to check.
        decorator_name (str): The name of the decorator to find.

    Returns:
        bool: True if the decorator exists, False otherwise.
    """
    return find_decorator_by_name(node, decorator_name) is not None


def get_string_keyword_arg(node: ast.Call, keyword_name: str) -> str:
    """
    Extract the value of a keyword argument from an ast.Call node if it is a string.

    Args:
        node (ast.Call): The AST node representing a function or decorator call.
        keyword_name (str): The name of the keyword argument to extract.

    Returns:
        str: The string value of the keyword argument.

    Raises:
        ValueError: If the keyword argument is missing or not a string.
        TypeError: If the node is not an ast.Call instance.
    """
    if not isinstance(node, ast.Call):
        raise TypeError(f"Expected ast.Call, got {type(node).__name__}")

    keyword_value = get_keyword_arg_value(node, keyword_name)

    if keyword_value is None:
        raise ValueError(f"Keyword argument '{keyword_name}' not found")

    if not (
        isinstance(keyword_value, ast.Constant) and isinstance(keyword_value.value, str)
    ):
        raise ValueError(f"Keyword argument '{keyword_name}' must be a string constant")

    return keyword_value.value
