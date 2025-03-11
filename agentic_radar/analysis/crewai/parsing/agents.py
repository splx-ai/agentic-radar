import ast
import os
import logging
from typing import Optional

from agentic_radar.analysis.crewai.models.tool import CrewAITool
from .utils import find_return_of_function_call, is_function_call


class AgentsCollector(ast.NodeVisitor):
    CREWAI_AGENT_CLASS = "Agent"

    def __init__(self, known_tool_aliases: set[str], predefined_tool_vars: dict[str, str], custom_tool_names: set[str]):
        self.known_tool_aliases = known_tool_aliases
        self.predefined_tool_vars = predefined_tool_vars
        self.custom_tool_names = custom_tool_names
        self.agent_tool_mapping = {}

    def _find_agent_return(self, node: ast.AST) -> Optional[ast.Call]:
        """
        Recursively search for and return the Agent constructor node from a return statement.
        
        Args:
            node: An AST node to search within
            
        Returns:
            The Agent constructor node if found, otherwise None
        """
        return find_return_of_function_call(node, self.CREWAI_AGENT_CLASS)
    
    def _is_agent_constructor(self, node) -> bool:
        """Check if a node is a call to Agent()"""
        return is_function_call(node, self.CREWAI_AGENT_CLASS)

    def _extract_agent_tools(self, agent_node: ast.Call) -> list[CrewAITool]:
        """
        Extract the list of tools from an Agent constructor node.
        
        Args:
            agent_node: The Agent constructor AST node
            
        Returns:
            A list of tool names used by this agent
        """
        tools = []
        
        # Look for the tools parameter in the Agent constructor
        for keyword in agent_node.keywords:
            if keyword.arg == 'tools':
                # Found the tools parameter
                tool_list = keyword.value
                
                if not isinstance(tool_list, ast.List):
                    logging.warning(f"Agent tools parameter is not a list: {tool_list}")
                    break

                # Handle tools=[tool1, tool2, ...] format
                for tool_node in tool_list.elts:
                    tool = self._extract_tool(tool_node)
                    if tool:
                        tools.append(tool)
            
        return tools

    def _extract_tool(self, node: ast.AST) -> Optional[CrewAITool]:
        """
        Extract the tool from a node in the tools list.
        
        Args:
            node: An AST node representing a tool
            
        Returns:
            The CrewAITool object if tool is identified identified, otherwise None
        """
        # Handle direct references like MyTools.some_tool
        if isinstance(node, ast.Attribute):
            if node.attr in self.custom_tool_names:
                return CrewAITool(name=node.attr, custom=True)
            elif node.attr in self.predefined_tool_vars:
                return CrewAITool(name=self.predefined_tool_vars[node.attr], custom=False)
        # Handle simple names like some_tool
        elif isinstance(node, ast.Name):
            if node.id in self.custom_tool_names:
                return CrewAITool(name=node.id, custom=True)
            elif node.id in self.predefined_tool_vars:
                return CrewAITool(name=self.predefined_tool_vars[node.id], custom=False)
        # Handle constructor calls of predefined tools like FileReadTool() or crewai_tools.FileReadTool()
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in self.known_tool_aliases:
                    return CrewAITool(name=node.func.id, custom=False)
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in self.known_tool_aliases:
                    return CrewAITool(name=node.func.attr, custom=False)
                
        return None
        
    def visit_FunctionDef(self, node):
        """Track functions that return an Agent instance."""

        agent_node = self._find_agent_return(node.body)
        if not agent_node:
            return
        
        agent_tools = self._extract_agent_tools(agent_node)
        self.agent_tool_mapping[node.name] = agent_tools

    def visit_Assign(self, node):
        """Track assignments that return an Agent instance."""
        if not isinstance(node.value, ast.Call):
            return
        
        if not self._is_agent_constructor(node.value):
            return
        
        # Handles cases like agent = Agent(...)
        for target in node.targets:
            if isinstance(target, ast.Name):
                agent_tools = self._extract_agent_tools(node.value)
                self.agent_tool_mapping[target.id] = agent_tools
        

    def collect(self, root_dir: str) -> dict[str, list[str]]:
        """Parses all Python modules in the given directory and collects agents together with their tools.

        Args:
            root_dir (str): Path to the codebase directory

        Returns:
            dict[str, list[str]]: A dictionary mapping agent names to their tool names
        """

        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r") as f:
                        tree = ast.parse(f.read())
                        self.visit(tree)

        return self.agent_tool_mapping
