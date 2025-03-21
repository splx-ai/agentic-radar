import ast
from typing import Optional

from agentic_radar.analysis.crewai.crew_process import CrewProcessType
from agentic_radar.analysis.crewai.parsing.utils import (
    find_return_of_function_call,
    is_function_call,
)
from agentic_radar.analysis.utils import walk_python_files


class CrewsVisitor(ast.NodeVisitor):
    CREWAI_CREW_CLASS = "Crew"
    CREWAI_CREW_BASE_CLASS_DECORATOR = "CrewBase"
    CREWAI_TASK_DECORATOR = "task"

    def __init__(self, tasks: set[str]):
        self.tasks = tasks  # For validation purposes
        self.decorated_tasks: list[str] = []
        self.crew_task_mapping: dict[str, list[str]] = {}
        self.crew_process_mapping: dict[str, CrewProcessType] = {}
        self.decorated_class_name: Optional[str] = None

    def _find_crew_return(self, node: ast.AST) -> Optional[ast.Call]:
        """
        Recursively search for and return the Crew constructor node from a return statement.

        Args:
            node: An AST node to search within

        Returns:
            The Crew constructor node if found, otherwise None
        """
        return find_return_of_function_call(node, self.CREWAI_CREW_CLASS)

    def _is_crew_constructor(self, node) -> bool:
        """Check if a node is a call to Crew()"""
        return is_function_call(node, self.CREWAI_CREW_CLASS)

    def _extract_crew_tasks(self, crew_node: ast.Call) -> list[str]:
        """
        Extract the list of tasks from a Crew constructor node.

        Args:
            crew_node: The Crew constructor AST node

        Returns:
            A list of task names used by this crew
        """
        tasks = []

        # Look for the tasks parameter in the Crew constructor
        for keyword in crew_node.keywords:
            if keyword.arg == "tasks":
                # Found the tasks parameter
                task_list = keyword.value

                if isinstance(task_list, ast.List):
                    # Handle tasks=[task1, task2, ...] format
                    for task_node in task_list.elts:
                        task_name = self._extract_task_name(task_node)
                        if task_name:
                            if task_name not in self.tasks:
                                print(
                                    f"Unrecognized task {task_name} for crew node {crew_node}"
                                )
                                continue
                            tasks.append(task_name)
                elif (
                    isinstance(task_list, ast.Attribute)
                    and isinstance(task_list.value, ast.Name)
                    and task_list.value.id == "self"
                    and task_list.attr == "tasks"
                ):
                    # Handle self.tasks format when using CrewAI decorators
                    decorated_tasks = self.decorated_tasks.copy()
                    self.decorated_tasks.clear()
                    return decorated_tasks
                else:
                    print(f"Unrecognized tasks parameter: {task_list}")
                    break

        return tasks

    def _extract_crew_process(self, crew_node: ast.Call) -> CrewProcessType:
        crew_process = CrewProcessType.SEQUENTIAL

        for keyword in crew_node.keywords:
            if keyword.arg == "process":
                process_node = keyword.value
                if not isinstance(process_node, (ast.Name, ast.Attribute)):
                    print(
                        f"Unrecognized type of process keyword argument: {process_node}. Falling back to SEQUENTIAL process."
                    )
                    break

                process_name = (
                    process_node.id
                    if isinstance(process_node, ast.Name)
                    else process_node.attr
                )

                if process_name == "sequential":
                    crew_process = CrewProcessType.SEQUENTIAL
                elif process_name == "hierarchical":
                    crew_process = CrewProcessType.HIERARCHICAL
                else:
                    print(f"Unrecognized crew process name: {process_name}")
                    break

        return crew_process

    def _extract_task_name(self, node: ast.AST) -> Optional[str]:
        """
        Extract the task name from a node in the tasks list.

        Args:
            node: An AST node representing a task

        Returns:
            The task name as a string if identified, otherwise None
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call) and isinstance(
            node.func, (ast.Name, ast.Attribute)
        ):
            return node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        return None

    def visit_ClassDef(self, node):
        """Tracks class definitions decorated with CrewBase decorator. Stores class name as a name that is to be used for the crew belonging to that class."""
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Name)
                and decorator.id == self.CREWAI_CREW_BASE_CLASS_DECORATOR
            ):
                self.decorated_class_name = node.name
                break

        self.generic_visit(node)
        self.decorated_class_name = None

    def visit_FunctionDef(self, node):
        """
        Tracks functions that return a Crew instance.
        Also tracks functions decorated with @task, in case decorators are used for registering agents, tasks and crews.
        """

        # Track decorated tasks
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Name)
                and decorator.id == self.CREWAI_TASK_DECORATOR
            ):
                self.decorated_tasks.append(node.name)
                return

        # Track Crew constructors
        crew_node = self._find_crew_return(node.body)
        if not crew_node:
            return

        if self.decorated_class_name:
            crew_name = (
                self.decorated_class_name
            )  # Take class name as crew name (we are inside subclass of CrewBase)
        else:
            crew_name = node.name  # Take function name as crew name

        crew_tasks = self._extract_crew_tasks(crew_node)
        self.crew_task_mapping[crew_name] = crew_tasks

        crew_process = self._extract_crew_process(crew_node)
        self.crew_process_mapping[crew_name] = crew_process

    def visit_Assign(self, node):
        """Track assignments that return an Agent instance."""
        if not isinstance(node.value, ast.Call):
            return

        if not self._is_crew_constructor(node.value):
            return

        # Handles cases like crew = Crew(...)
        for target in node.targets:
            if isinstance(target, ast.Name):
                crew_tasks = self._extract_crew_tasks(node.value)
                self.crew_task_mapping[target.id] = crew_tasks

                crew_process = self._extract_crew_process(node.value)
                self.crew_process_mapping[target.id] = crew_process


def collect_crews(
    root_dir: str, tasks: set[str]
) -> tuple[dict[str, list[str]], dict[str, CrewProcessType]]:
    """Parses all Python modules in the given directory and collects crews together with corresponding tasks.

    Args:
        root_dir (str): Path to the codebase directory
        tasks: (set[str]): Set of all task names

    Returns:
        tuple[dict[str, list[str]], dict[str, CrewProcessType]]: Tuple consisting of two elements: 1. crew-tasks mapping, 2. crew-process mapping
    """
    crew_task_mapping: dict[str, list[str]] = {}
    crew_process_mapping: dict[str, CrewProcessType] = {}

    for file in walk_python_files(root_dir):
        with open(file, "r") as f:
            try:
                tree = ast.parse(f.read())
            except Exception as e:
                print(f"Cannot parse Python module: {file}. Error: {e}")
                continue
            crews_visitor = CrewsVisitor(tasks)
            crews_visitor.visit(tree)
            crew_task_mapping |= crews_visitor.crew_task_mapping
            crew_process_mapping |= crews_visitor.crew_process_mapping

    return crew_task_mapping, crew_process_mapping
