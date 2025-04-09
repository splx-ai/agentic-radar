import ast
from typing import Optional

from pydantic import ValidationError

from agentic_radar.analysis.crewai.models import (
    CrewAIAgent,
    CrewAITool,
    PartialCrewAIAgent,
)
from agentic_radar.analysis.crewai.parsing.utils import (
    find_return_of_function_call,
    get_bool_kwarg_value,
    get_string_kwarg_value,
    is_function_call,
)
from agentic_radar.analysis.crewai.parsing.yaml_config import (
    collect_agents_from_config,
)
from agentic_radar.analysis.crewai.tool_descriptions import (
    get_crewai_tools_descriptions,
)
from agentic_radar.analysis.utils import walk_python_files


class AgentsVisitor(ast.NodeVisitor):
    CREWAI_AGENT_CLASS = "Agent"

    def __init__(
        self,
        known_tool_aliases: set[str],
        predefined_tools: dict[str, CrewAITool],
        custom_tools: dict[str, CrewAITool],
    ):
        self.known_tool_aliases = known_tool_aliases
        self.predefined_tools = predefined_tools
        self.custom_tools = custom_tools

        self.crewai_tool_descriptions = get_crewai_tools_descriptions()

        self.yaml_config_paths: list[str] = []
        self.agents: dict[str, PartialCrewAIAgent] = {}

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
            A list of tools
        """
        tools = []

        # Look for the tools parameter in the Agent constructor
        for keyword in agent_node.keywords:
            if keyword.arg == "tools":
                # Found the tools parameter
                tool_list = keyword.value

                if not isinstance(tool_list, ast.List):
                    print(f"Agent tools parameter is not a list: {tool_list}")
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
            if node.attr in self.custom_tools:
                return self.custom_tools[node.attr]
            elif node.attr in self.predefined_tools:
                return self.predefined_tools[node.attr]
        # Handle simple names like some_tool
        elif isinstance(node, ast.Name):
            if node.id in self.custom_tools:
                return self.custom_tools[node.id]
            elif node.id in self.predefined_tools:
                return self.predefined_tools[node.id]
        # Handle constructor calls of predefined tools like FileReadTool() or crewai_tools.FileReadTool()
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in self.known_tool_aliases:
                    description = self.crewai_tool_descriptions.get(node.func.id, "")
                    return CrewAITool(
                        name=node.func.id, custom=False, description=description
                    )
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in self.known_tool_aliases:
                    description = self.crewai_tool_descriptions.get(node.func.attr, "")
                    return CrewAITool(
                        name=node.func.attr, custom=False, description=description
                    )

        return None

    def _handle_string_node(self, s: str) -> None:
        if not s.endswith(".yaml") and not s.endswith(".yml"):
            return

        self.yaml_config_paths.append(s)

    def _extract_agent(self, agent_node: ast.Call) -> PartialCrewAIAgent:
        """
        Extract the agent from an Agent constructor node.

        Args:
            agent_node: The Agent constructor AST node

        Returns:
            A PartialCrewAIAgent object
        """

        role = get_string_kwarg_value(agent_node, "role")
        goal = get_string_kwarg_value(agent_node, "goal")
        backstory = get_string_kwarg_value(agent_node, "backstory")
        system_template = get_string_kwarg_value(agent_node, "system_template")
        prompt_template = get_string_kwarg_value(agent_node, "prompt_template")
        response_template = get_string_kwarg_value(agent_node, "response_template")
        use_system_prompt = get_bool_kwarg_value(agent_node, "use_system_prompt")
        llm = get_string_kwarg_value(agent_node, "llm")
        tools = self._extract_agent_tools(agent_node)

        if use_system_prompt is None:
            use_system_prompt = True

        return PartialCrewAIAgent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            llm=llm,
            system_template=system_template,
            prompt_template=prompt_template,
            response_template=response_template,
            use_system_prompt=use_system_prompt,
        )

    def visit_FunctionDef(self, node):
        """Track functions that return an Agent instance."""

        agent_node = self._find_agent_return(node.body)
        if not agent_node:
            self.generic_visit(node)
            return

        try:
            agent = self._extract_agent(agent_node)
            self.agents[node.name] = agent
        except (ValueError, TypeError) as e:
            print(f"Cannot extract agent {ast.dump(agent_node)}. Error: {e}")

        self.generic_visit(node)

    def visit_Assign(self, node):
        """Track assignments that return an Agent instance."""
        if not isinstance(node.value, ast.Call):
            self.generic_visit(node)
            return

        if not self._is_agent_constructor(node.value):
            self.generic_visit(node)
            return

        # Handles cases like agent = Agent(...)
        for target in node.targets:
            if isinstance(target, ast.Name):
                try:
                    agent = self._extract_agent(node.value)
                except (ValueError, TypeError) as e:
                    print(f"Cannot extract agent {ast.dump(node.value)}. Error: {e}")
                    continue

                self.agents[target.id] = agent

        self.generic_visit(node)

    def visit_Constant(self, node):  # To visit strings in Python >= 3.8
        """Tracks strings that represent path to yaml configuration files."""
        if isinstance(node.value, str):
            self._handle_string_node(node.value)

    def visit_Str(self, node):  # To visit strings in Python < 3.8
        """Tracks strings that represent path to yaml configuration files."""
        self._handle_string_node(node.s)


def collect_agents(
    root_dir: str,
    known_tool_aliases: set[str],
    predefined_tools: dict[str, CrewAITool],
    custom_tools: dict[str, CrewAITool],
) -> dict[str, CrewAIAgent]:
    """Parses all Python modules and YAML configs in the given directory and collects agents.

    Args:
        root_dir (str): Path to the codebase directory
        known_tool_aliases (set[str]): Set of predefined tool aliases parsed from import statements
        predefined_tools (dict[str, CrewAITool]): Dictionary mapping variable name to predefined tool
        custom_tools (dict[str, CrewAITool]): Dictionary mapping variable name to custom tool

    Returns:
        dict[str, CrewAIAgent]: A dictionary mapping agent variable to CrewAIAgent object
    """
    all_agents: dict[str, CrewAIAgent] = {}
    yaml_file_to_agents: dict[
        str, dict[str, PartialCrewAIAgent]
    ] = collect_agents_from_config(root_dir)

    for file in walk_python_files(root_dir):
        with open(file, "r") as f:
            try:
                tree = ast.parse(f.read())
            except Exception as e:
                print(f"Cannot parse Python module: {file}. Error: {e}")
                continue
            agents_visitor = AgentsVisitor(
                known_tool_aliases=known_tool_aliases,
                predefined_tools=predefined_tools,
                custom_tools=custom_tools,
            )
            agents_visitor.visit(tree)
            code_agents = agents_visitor.agents

            # Add agents from found YAML config files
            for found_config_path in agents_visitor.yaml_config_paths:
                for (
                    config_path,
                    yaml_agents,
                ) in yaml_file_to_agents.items():
                    if found_config_path not in config_path:
                        continue
                    for agent_name, yaml_agent in yaml_agents.items():
                        if agent_name in code_agents:
                            code_agent = code_agents[agent_name]
                            try:
                                agent = CrewAIAgent.from_partial_agents(
                                    code_agent, yaml_agent
                                )
                            except (ValidationError, ValueError) as e:
                                print(
                                    f"Cannot merge agent {agent_name} from code and YAML config. Error: {e}"
                                )
                                continue
                        else:
                            try:
                                agent = CrewAIAgent.from_partial_agent(yaml_agent)
                            except (ValidationError, ValueError) as e:
                                print(
                                    f"Cannot create agent {agent_name} from YAML config: {yaml_agent}. Error: {e}"
                                )
                                continue

                        all_agents[agent_name] = agent

            # Add agents from code
            for agent_name, code_agent in code_agents.items():
                if agent_name in all_agents:
                    continue
                try:
                    agent = CrewAIAgent.from_partial_agent(code_agent)
                except (ValidationError, ValueError) as e:
                    print(
                        f"Cannot create agent {agent_name} from code: {code_agent}. Error: {e}"
                    )
                    continue

                all_agents[agent_name] = agent

    return all_agents
