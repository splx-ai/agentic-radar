import ast

from pydantic import ValidationError

from ...utils import walk_python_files
from ..exceptions import InvalidAgentConstructorError, InvalidHandoffDefinitionError
from ..models import Agent, Tool
from .ast_utils import (
    get_keyword_arg_value,
    get_nth_arg_value,
    get_simple_identifier_name,
    get_string_keyword_arg,
    is_function_call,
    is_simple_identifier,
)


class AgentsVisitor(ast.NodeVisitor):
    AGENT_CLASS_NAME = "Agent"
    HANDOFF_FUNCTION_NAME = "handoff"

    def __init__(
        self, tool_assignments: dict[str, Tool], predefined_tools: dict[str, Tool]
    ):
        super().__init__()
        self.tool_assignments = tool_assignments
        self.predefined_tools = predefined_tools
        self.handoff_assignments: dict[str, str] = {}
        self.agent_assignments: dict[str, Agent] = {}

    def visit_Assign(self, node):
        if is_function_call(node.value, self.AGENT_CLASS_NAME):
            self._visit_agent_assignment(node)
        elif is_function_call(node.value, self.HANDOFF_FUNCTION_NAME):
            self._visit_handoff_assignment(node)

    def _visit_agent_assignment(self, node: ast.Assign) -> None:
        assert isinstance(node.value, ast.Call)

        try:
            agent = self._extract_agent(node.value)
        except InvalidAgentConstructorError as e:
            print(
                f"Invalid Agent constructor for agent: {ast.dump(node.value)}. Error: {e}"
            )
            return

        for target in node.targets:
            if not is_simple_identifier(target):
                continue

            target_name = get_simple_identifier_name(target)
            self.agent_assignments[target_name] = agent

    def _visit_handoff_assignment(self, node: ast.Assign) -> None:
        try:
            handoff = self._extract_handoff(node.value)
        except InvalidHandoffDefinitionError as e:
            print(f"Invalid handoff definition: {ast.dump(node.value)}. Error: {e}")
            return

        for target in node.targets:
            if not is_simple_identifier(target):
                continue

            target_name = get_simple_identifier_name(target)
            self.handoff_assignments[target_name] = handoff

    def _extract_agent(self, agent_node: ast.Call) -> Agent:
        try:
            name = self._extract_agent_name(agent_node)
            tools = self._extract_agent_tools(agent_node)
            handoffs = self._extract_agent_handoffs(agent_node)
            return Agent(name=name, tools=tools, handoffs=handoffs)
        except (ValueError, ValidationError) as e:
            raise InvalidAgentConstructorError from e

    def _extract_agent_name(self, agent_node: ast.Call) -> str:
        name_node = get_keyword_arg_value(agent_node, "name")
        if not name_node:
            raise ValueError(
                f"Agent constructor node is missing 'name' keyword argument: {ast.dump(agent_node)}"
            )

        if isinstance(name_node, ast.Constant) and isinstance(name_node.value, str):
            return name_node.value
        elif isinstance(name_node, ast.Str):
            return name_node.s
        else:
            raise ValueError(
                f"Unrecognized type of name node for Agent: {type(name_node)}. Node representing a string is required."
            )

    def _extract_agent_tools(self, agent_node: ast.Call) -> list[Tool]:
        tools_node = get_keyword_arg_value(agent_node, "tools")
        if not tools_node or not isinstance(tools_node, ast.List):
            return []

        tools = []
        for tool_node in tools_node.elts:
            try:
                tool = self._extract_agent_tool(tool_node)
                tools.append(tool)
            except (ValueError, TypeError) as e:
                print(
                    f"Could not parse agent tool node {ast.dump(tool_node)}. Error: {e}"
                )

        return tools

    def _extract_agent_handoffs(self, agent_node: ast.Call) -> list[str]:
        handoffs_node = get_keyword_arg_value(agent_node, "handoffs")
        if not handoffs_node or not isinstance(handoffs_node, ast.List):
            return []

        handoffs = []
        for handoff_node in handoffs_node.elts:
            try:
                handoff = self._extract_handoff(handoff_node)
                handoffs.append(handoff)
            except ValueError as e:
                print(
                    f"Could not parse agent handoff node {ast.dump(handoff_node)}. Error: {e}"
                )

        return handoffs

    def _extract_agent_tool(self, tool_node: ast.AST) -> Tool:
        if is_simple_identifier(tool_node):
            identifier_name = get_simple_identifier_name(tool_node)
            if identifier_name not in self.tool_assignments:
                raise ValueError(f"Unknown custom tool: {identifier_name}")
            return self.tool_assignments[identifier_name]
        elif isinstance(tool_node, ast.Call) and is_simple_identifier(tool_node.func):
            func_name = get_simple_identifier_name(tool_node.func)

            if func_name == "as_tool":
                if (
                    isinstance(tool_node.func, ast.Attribute)
                    and isinstance(tool_node.func.value, ast.Name)
                    and tool_node.func.value.id in self.agent_assignments
                ):
                    # Remove as_tool agent assignment (TODO: handle case of agent imports)
                    del self.agent_assignments[tool_node.func.value.id]
                return self._extract_as_tool(tool_node)

            if func_name not in self.predefined_tools:
                raise ValueError(f"Unknown predefined tool: {func_name}")
            return self.predefined_tools[func_name]
        else:
            raise TypeError(f"Unknown tool node type: {type(tool_node)}")

    def _extract_handoff(self, handoff_node: ast.AST) -> str:
        """Extract handoffs from AST node.
        Examples of handoffs in source code which will get recognized by this method: `myagent` (variable which holds an agent), `myhandoff` (variable which holds a handoff object), `handoff(myagent)`, `handoff(agent=myagent)`

        Args:
            handoff_node (ast.AST): AST node which represents a handoff

        Returns:
            str: name of the target agent for the handoff
        """
        if is_simple_identifier(handoff_node):
            handoff_identifier = get_simple_identifier_name(handoff_node)
            if handoff_identifier in self.handoff_assignments:
                return self.handoff_assignments[handoff_identifier]
            else:
                return handoff_identifier
        elif isinstance(handoff_node, ast.Call):
            if not is_simple_identifier(handoff_node.func):
                raise ValueError(
                    f"Unrecognized handoff function node: {ast.dump(handoff_node)}"
                )
            handoff_function_name = get_simple_identifier_name(handoff_node.func)
            if handoff_function_name != self.HANDOFF_FUNCTION_NAME:
                raise ValueError(
                    f"Invalid handoff function name: {handoff_function_name}"
                )

            handoff_agent_node = get_keyword_arg_value(
                handoff_node, keyword_name="agent"
            )
            if not handoff_agent_node:
                handoff_agent_node = get_nth_arg_value(handoff_node, n=0)
            if not is_simple_identifier(handoff_agent_node):
                raise ValueError(
                    f"Unrecognized handoff agent node: {ast.dump(handoff_agent_node)}"
                )

            handoff_agent_identifier = get_simple_identifier_name(handoff_agent_node)
            return handoff_agent_identifier
        else:
            raise TypeError(f"Unrecognized handoff node: {ast.dump(handoff_node)}")

    def _extract_as_tool(self, as_tool_node: ast.Call) -> Tool:
        tool_name = get_string_keyword_arg(as_tool_node, "tool_name")

        try:
            tool_description = get_string_keyword_arg(as_tool_node, "tool_description")
        except (TypeError, ValueError):
            tool_description = ""

        return Tool(name=tool_name, custom=True, description=tool_description)


def collect_agent_assignments(
    root_dir: str, tool_assignments: dict[str, Tool], predefined_tools: dict[str, Tool]
) -> dict[str, Agent]:
    agent_assignments: dict[str, Agent] = {}
    for file in walk_python_files(root_dir):
        with open(file, "r") as f:
            try:
                tree = ast.parse(f.read())
            except Exception as e:
                print(f"Cannot parse Python module: {file}. Error: {e}")
                continue
            agents_visitor = AgentsVisitor(
                tool_assignments=tool_assignments, predefined_tools=predefined_tools
            )
            agents_visitor.visit(tree)
            agent_assignments |= agents_visitor.agent_assignments

    return agent_assignments
