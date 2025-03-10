import ast
import os
import logging
from typing import Optional

from .utils import find_return_of_function_call, is_function_call

class TasksCollector(ast.NodeVisitor):
    CREWAI_TASK_CLASS = "Task"

    def __init__(self, agents: set[str]):
        self.agents = agents
        self.task_agent_mapping = {}

    def _find_task_return(self, node: ast.AST) -> Optional[ast.Call]:
        """
        Recursively search for and return the Task constructor node from a return statement.
        
        Args:
            node: An AST node to search within
            
        Returns:
            The Task constructor node if found, otherwise None
        """
        return find_return_of_function_call(node, self.CREWAI_TASK_CLASS)
        
    def _is_task_constructor(self, node) -> bool:
        """Check if a node is a call to Task()"""
        return is_function_call(node, self.CREWAI_TASK_CLASS)

    def _extract_task_agent(self, task_node: ast.Call) -> Optional[str]:
        """
        Extract the agent name from a Task constructor node.
        
        Args:
            task_node: The Task constructor AST node
            
        Returns:
            The agent name used by this task if found, otherwise None
        """
        def get_agent_name(agent_node: ast.AST) -> Optional[str]:
            if isinstance(agent_node, ast.Name):
                return agent_node.id
            elif isinstance(agent_node, ast.Call) and isinstance(agent_node.func, (ast.Name, ast.Attribute)):
                return agent_node.func.id if isinstance(agent_node.func, ast.Name) else agent_node.func.attr
            return None

        for keyword in task_node.keywords:
            if keyword.arg == 'agent':
                agent_node = keyword.value
                agent_name = get_agent_name(agent_node)
                if agent_name and agent_name in self.agents:
                    return agent_name
                logging.warning(f"Unknown or unexpected agent {agent_node} for task {task_node}")
                return None
        return None
        
    def visit_FunctionDef(self, node):
        """Track functions that return a Task instance."""

        task_node = self._find_task_return(node.body)
        if not task_node:
            return
        
        agent = self._extract_task_agent(task_node)
        if not agent:
            logging.warning(f"Task {node.name} does not specify an agent")
            return
        
        self.task_agent_mapping[node.name] = agent

    def visit_Assign(self, node):
        """Track assignments that return a Task instance."""
        if not isinstance(node.value, ast.Call):
            return
        
        if not self._is_task_constructor(node.value):
            return
        
        # Handles cases like task = Task(...)
        for target in node.targets:
            if isinstance(target, ast.Name):
                agent = self._extract_task_agent(node.value)
                if not agent:
                    logging.warning(f"Task {target.id} does not specify an agent")
                    return
                self.task_agent_mapping[target.id] = agent        

    def collect(self, root_dir: str) -> dict[str, str]:
        """Parses all Python modules in the given directory and collects task-agent mappings.

        Args:
            root_dir (str): Path to the codebase directory

        Returns:
            dict[str, str]: A dictionary mapping task names to agent names
        """

        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r") as f:
                        tree = ast.parse(f.read())
                        self.visit(tree)

        return self.task_agent_mapping
