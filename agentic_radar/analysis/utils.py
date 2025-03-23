import os
from typing import Generator, Optional


def walk_files(
    root_dir: str, extensions: set[str], blacklist: Optional[list[str]] = None
) -> Generator[str, None, None]:
    if blacklist is None:
        blacklist = [".venv"]
    for root, dirs, files in os.walk(root_dir):
        # Remove blacklisted directories from the search
        dirs[:] = [d for d in dirs if d not in blacklist]
        for file in files:
            _, file_ext = os.path.splitext(file)
            # Only yield files with certain extensions
            if file_ext in extensions:
                yield os.path.join(root, file)


def walk_python_files(
    root_dir: str, blacklist: Optional[list[str]] = None
) -> Generator[str, None, None]:
    """
    Walk through all Python files in a directory, optionally skipping blacklisted folders.
    :param root_dir: The base directory to start the search.
    :param blacklist: A list of folder names to skip. Defaults to ['.venv'].
    :return: A generator yielding paths to Python files.
    """
    if blacklist is None:
        blacklist = [".venv"]
    allowed_extensions = [".py"]
    yield from walk_files(
        root_dir=root_dir, extensions=set(allowed_extensions), blacklist=blacklist
    )


def walk_python_files_and_notebooks(
    root_dir: str, blacklist: Optional[list[str]] = None
) -> Generator[str, None, None]:
    """
    Walk through all Python files and Jupyter notebooks in a directory, optionally skipping blacklisted folders.
    :param root_dir: The base directory to start the search.
    :param blacklist: A list of folder names to skip. Defaults to ['.venv'].
    :return: A generator yielding paths to Python files and Jupyter notebooks.
    """
    if blacklist is None:
        blacklist = [".venv"]
    allowed_extensions = [".py", ".ipynb"]
    yield from walk_files(
        root_dir=root_dir, extensions=set(allowed_extensions), blacklist=blacklist
    )


def walk_yaml_files(
    root_dir: str, blacklist: Optional[list[str]] = None
) -> Generator[str, None, None]:
    """
    Walk through all YAML files in a directory, optionally skipping blacklisted folders.
    :param root_dir: The base directory to start the search.
    :param blacklist: A list of folder names to skip. Defaults to ['.venv'].
    :return: A generator yielding paths to YAML files.
    """
    if blacklist is None:
        blacklist = [".venv"]
    allowed_extensions = [".yaml", ".yml"]
    yield from walk_files(
        root_dir=root_dir, extensions=set(allowed_extensions), blacklist=blacklist
    )
