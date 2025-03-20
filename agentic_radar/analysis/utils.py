import os
from typing import Generator


def walk_python_files(root_dir: str, blacklist: list[str] = [".venv"]) -> Generator[str, None, None]:
    """
    Walk through all Python files in a directory, optionally skipping blacklisted folders.

    :param root_dir: The base directory to start the search.
    :param blacklist: A list of folder names to skip. Defaults to ['.venv'].
    :return: A generator yielding paths to Python files.
    """

    for root, dirs, files in os.walk(root_dir):
        # Remove blacklisted directories from the search
        dirs[:] = [d for d in dirs if d not in blacklist]

        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)

def walk_python_files_and_notebooks(root_dir: str, blacklist: list[str] = [".venv"]) -> Generator[str, None, None]:
    """
    Walk through all Python files and Jupyter notebooks in a directory, optionally skipping blacklisted folders.

    :param root_dir: The base directory to start the search.
    :param blacklist: A list of folder names to skip. Defaults to ['.venv'].
    :return: A generator yielding paths to Python files and Jupyter notebooks.
    """

    for root, dirs, files in os.walk(root_dir):
        # Remove blacklisted directories from the search
        dirs[:] = [d for d in dirs if d not in blacklist]

        for file in files:
            if file.endswith(".py") or file.endswith(".ipynb"):
                yield os.path.join(root, file)
