import ast

from ..exceptions import InvalidAgentConstructorError
from ..models import Agent
from .ast_utils import get_simple_identifier_name, is_simple_identifier


class AgentsVisitor(ast.NodeVisitor):
    AGENT_CLASS_NAME = "Agent"

    def __init__(self):
        super().__init__()
        self.agent_assignments: dict[str, Agent] = {}
    
    def visit_Assign(self, node):
        if not isinstance(node.value, ast.Call):
            return
        
        if not isinstance(node.value.func, (ast.Name, ast.Attribute)):
            return

        func_name = node.value.func.id if isinstance(node.value.func, ast.Name) else node.value.func.attr

        if func_name != self.AGENT_CLASS_NAME:
            return

        try:
            agent = self._extract_agent(node.value)
        except InvalidAgentConstructorError:
            print(f"Invalid Agent constructor for agent: {ast.dump(node.value)}")
            return
        
        for target in node.targets:
            if not is_simple_identifier(target):
                continue

            target_name = get_simple_identifier_name(target)
            self.agent_assignments[target_name] = agent


    
    def _extract_agent(self, agent_node: ast.Call) -> Agent:
        pass        