import ast
from typing import Generator, Optional, Union

from pydantic import BaseModel

from agentic_radar.analysis.utils import walk_python_files


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


def get_string_keyword_arg(node: ast.Call, keyword_name: str) -> Optional[str]:
    """
    Extract the value of a keyword argument from an ast.Call node if it is a string.

    Args:
        node (ast.Call): The AST node representing a function or decorator call.
        keyword_name (str): The name of the keyword argument to extract.

    Returns:
        Optional[str]: The string value of the keyword argument, or None if the keyword argument is missing.

    Raises:
        TypeError: If the node is not an ast.Call instance.
        ValueError: If the keyword argument is not a string.
    """
    if not isinstance(node, ast.Call):
        raise TypeError(f"Expected ast.Call, got {type(node).__name__}")

    keyword_value = get_keyword_arg_value(node, keyword_name)

    if keyword_value is None:
        return None

    if not (
        isinstance(keyword_value, ast.Constant) and isinstance(keyword_value.value, str)
    ):
        raise ValueError(f"Keyword argument '{keyword_name}' must be a string constant")

    return keyword_value.value


class SimpleFunctionCallAssignment(BaseModel):
    """
    Represents a simple function call assignment in Python code.
    Example of a simple function call assignment:
    ```python
    my_var = my_function(arg1, arg2, kwarg1=value1, kwarg2=value2)
    ```
    """

    target: str
    function_name: str
    args: list[Union[str, int, float, bool, list, None]]
    kwargs: dict[str, Union[str, int, float, bool, list, None]]

    def __str__(self) -> str:
        args_str = ", ".join(repr(arg) for arg in self.args)
        kwargs_str = ", ".join(f"{k}={v!r}" for k, v in self.kwargs.items())
        return f"{self.target} = {self.function_name}({args_str}, {kwargs_str})"

    def resolve_arg_or_kwarg(self, index: int, key: str):
        """
        Resolve the value of an argument or keyword argument by index or key.
        Tries to return the value of the positional argument at given index first,
        then the keyword argument at the given key.
        If neither is found, returns None.

        Args:
            index (int): The index of the positional argument to resolve.
            key (str): The key of the keyword argument to resolve.

        Returns:
            Union[str, int, float, bool, None]: The resolved value, or None if not found.
        """
        if key in self.kwargs:
            return self.kwargs[key]
        if 0 <= index < len(self.args):
            return self.args[index]
        return None


def parse_simple_function_call_assignment(
    node: ast.AST
) -> Optional[SimpleFunctionCallAssignment]:
    """
    Check if the node is a simple function call assignment and extract its details.
    Identifiers are converted to strings, and constants are converted to their values.

    Args:
        node (ast.AST): The AST node to check.

    Returns:
        Optional[SimpleFunctionCallAssignment]: An instance of SimpleFunctionCallAssignment if the node matches,
        otherwise None.
    """
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target = node.targets[0]
        if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
            if not is_simple_identifier(node.value.func):
                return None
            function_name = get_simple_identifier_name(node.value.func)

            def extract_value(val: ast.AST) -> Union[str, int, float, bool, list, None]:
                if isinstance(val, ast.Constant):
                    return val.value
                elif is_simple_identifier(val):
                    return get_simple_identifier_name(val)
                elif isinstance(val, (ast.List, ast.Tuple)):
                    return [extract_value(item) for item in val.elts]
                else:
                    return None

            args = [extract_value(arg) for arg in node.value.args]
            kwargs = {
                kw.arg: extract_value(kw.value) for kw in node.value.keywords if kw.arg
            }
            return SimpleFunctionCallAssignment(
                target=target.id, function_name=function_name, args=args, kwargs=kwargs
            )
    return None


def walk_and_parse_python_files(
    root_dir: str
) -> Generator[tuple[str, ast.AST], None, None]:
    for file_path in walk_python_files(root_dir):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=file_path)
                yield file_path, tree
            except Exception:
                continue
