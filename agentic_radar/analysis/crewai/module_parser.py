import ast

from agentic_radar.analysis.crewai.models import CrewAIGraph, CrewAINodeType

class CrewAIModuleParser(ast.NodeVisitor):
    def __init__(self, crewai_graph: CrewAIGraph):
        self.crewai_graph = crewai_graph
        self.known_agent_aliases = {"Agent"}
        self.known_tool_aliases = set()
        self.crewai_tools_import_name = None
        self.crewai_import_name = None
        self.tool_assignments = {}

    def visit_ImportFrom(self, node):
        """Track imports like 'from crewai import Agent' and 'from crewai_tools import FileReadTool'."""
        if node.module == "crewai":
            for alias in node.names:
                if alias.name == "Agent":
                    self.known_agent_aliases.add(alias.asname or alias.name)

        if node.module == "crewai_tools":
            for alias in node.names:
                tool_name = alias.asname or alias.name
                self.known_tool_aliases.add(tool_name)

    def visit_Import(self, node):
        """Track 'import crewai' and 'import crewai_tools'."""
        for alias in node.names:
            if alias.name == "crewai":
                self.crewai_import_name = alias.asname or alias.name
            elif alias.name == "crewai_tools":
                self.crewai_tools_import_name = alias.asname or alias.name

    def visit_Assign(self, node):
        """Detect assignments of Agents and Tools, and extract agent-tool mapping."""
        if not isinstance(node.value, ast.Call):
            return
        func = node.value.func

        # Detect tools assigned to a constructor call (FileReadTool(), DirectoryReadTool(), etc.)
        if isinstance(func, ast.Name) and func.id in self.known_tool_aliases:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.tool_assignments[target.id] = func.id

        # Detect tools assigned via constructor call with package prefix (eg. crewai_tools.XYZTool)
        elif (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == self.crewai_tools_import_name
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.tool_assignments[target.id] = func.attr

        # Detect agents and extract tool mappings
        elif isinstance(func, ast.Name) and func.id in self.known_agent_aliases:
            tools = self._extract_tools_from_agent(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.crewai_graph.create_nodes_and_connect_with_many(
                        src_node=target.id,
                        src_node_type=CrewAINodeType.AGENT,
                        dest_nodes=tools,
                        dest_nodes_type=CrewAINodeType.TOOL,
                    )
        elif (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == self.crewai_import_name
            and func.attr in self.known_agent_aliases
        ):
            tools = self._extract_tools_from_agent(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.crewai_graph.create_nodes_and_connect_with_many(
                        src_node=target.id,
                        src_node_type=CrewAINodeType.AGENT,
                        dest_nodes=tools,
                        dest_nodes_type=CrewAINodeType.TOOL,
                    )

    def visit_FunctionDef(self, node):
        """
        Detect functions which contain Agent constructor calls in their body and extract corresponding agents and tools.
        TODO: Add more complex logic for finding Agents defined in this manner.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id in self.known_agent_aliases:
                    tools = self._extract_tools_from_agent(child)
                    self.crewai_graph.create_nodes_and_connect_with_many(
                        src_node=node.name,
                        src_node_type=CrewAINodeType.AGENT,
                        dest_nodes=tools,
                        dest_nodes_type=CrewAINodeType.TOOL,
                    )

    def _extract_tools_from_agent(self, agent_constructor_node: ast.Call) -> list[str]:
        """Extract associated tools from Agent constructor call (Agent(...))."""
        func = agent_constructor_node.func
        assert (
            isinstance(func, ast.Name)
            and func.id in self.known_agent_aliases
            or isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.attr in self.known_agent_aliases
        )

        tool_names = []

        # Extract tools from the 'tools' keyword argument
        for kw in agent_constructor_node.keywords:
            if kw.arg == "tools" and isinstance(kw.value, ast.List):
                for item in kw.value.elts:
                    if isinstance(item, ast.Name) and item.id in self.tool_assignments:
                        if item.id not in self.tool_assignments:
                            raise ValueError(
                                f"Unknown tool (assigment is missing): {item.id}"
                            )
                        tool_names.append(self.tool_assignments[item.id])
                    elif isinstance(item, ast.Call):
                        tool_name = (
                            item.func.id
                            if isinstance(item.func, ast.Name)
                            else item.func.attr
                        )
                        if tool_name not in self.known_tool_aliases:
                            raise ValueError(
                                f"Unknown tool (never imported): {tool_name}"
                            )
                        tool_names.append(tool_name)

        return tool_names

    def parse(self, file_path: str):
        """
        Parse a Python file starting from the root (Module) node, extract agents, tools, tasks and their connections.
        Agents, tools and tasks are stored internally in a CrewAIGraph instance.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)

        self.visit(tree)



if __name__ == "__main__":
    # Example usage:
    file_path = "examples/crewai/job_posting.py"
    parser = CrewAIModuleParser()
    parser.parse(file_path)

    print("Agent-Tool Mapping:", parser.crewai_graph)
