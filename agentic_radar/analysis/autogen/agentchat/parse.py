import ast

from agentic_radar.analysis.ast_utils import parse_simple_function_call_assignment

from .models import Agent, FunctionDefinition, FunctionTool, ModelClient, Team, TeamType

AUTOGEN_MODELS_IMPORT_PREFIX = "autogen_ext.models"


def find_model_client_imports(trees: list[ast.AST]) -> set[str]:
    imports = set()
    for tree in trees:
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith(AUTOGEN_MODELS_IMPORT_PREFIX):
                    for alias in node.names:
                        imports.add(alias.asname if alias.asname else alias.name)
    return imports


def find_all_functions(trees: list[ast.AST]) -> dict[str, FunctionDefinition]:
    functions = {}
    for tree in trees:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_def = FunctionDefinition(
                    name=node.name,
                    description=ast.get_docstring(node) or "",
                )
                functions[func_def.name] = func_def
    return functions


def find_model_client_assignments(
    trees: list[ast.AST], imported_model_clients: set[str]
) -> dict[str, ModelClient]:
    model_clients = {}
    for tree in trees:
        for node in ast.walk(tree):
            simple_function_call_assignment = parse_simple_function_call_assignment(
                node
            )

            if not simple_function_call_assignment:
                continue

            if (
                simple_function_call_assignment.function_name
                not in imported_model_clients
            ):
                continue

            model = simple_function_call_assignment.kwargs.get("model")
            if not isinstance(model, str):
                model = ""

            model_client = ModelClient(
                name=simple_function_call_assignment.function_name, model=model
            )
            model_clients[simple_function_call_assignment.target] = model_client
    return model_clients


def find_function_tool_assignments(
    trees: list[ast.AST], all_functions: dict[str, FunctionDefinition]
) -> dict[str, FunctionTool]:
    """
    Tracks assignments like:
    function_tool = FunctionTool(some_function, description="...")
    """
    function_tools = {}
    for tree in trees:
        for node in ast.walk(tree):
            simple_function_call_assignment = parse_simple_function_call_assignment(
                node
            )
            if not simple_function_call_assignment:
                continue

            if simple_function_call_assignment.function_name != "FunctionTool":
                continue

            if len(simple_function_call_assignment.args) < 1:
                continue

            function_name = simple_function_call_assignment.resolve_arg_or_kwarg(
                0, "func"
            )
            if not isinstance(function_name, str) or function_name not in all_functions:
                continue
            function_def = all_functions[function_name]

            description = simple_function_call_assignment.resolve_arg_or_kwarg(
                1, "description"
            )
            if not isinstance(description, str):
                description = ""

            name = simple_function_call_assignment.resolve_arg_or_kwarg(2, "name")
            if not isinstance(name, str):
                name = ""

            function_tools[simple_function_call_assignment.target] = FunctionTool(
                name=name or function_def.name,
                description=description or function_def.description,
            )

    return function_tools


def find_agent_assignments(
    trees: list[ast.AST],
    model_clients: dict[str, ModelClient],
    function_tools: dict[str, FunctionTool],
    all_functions: dict[str, FunctionDefinition],
) -> dict[str, Agent]:
    """
    Tracks assignments like:
    agent = Agent(name="MyAgent", tools=[tool1, tool2], model_client=model_client, system_message="...")
    """

    KNOWN_AGENT_CLASSES = {
        "AssistantAgent",
        "UserProxyAgent",
        "CodeExecutorAgent",
        "OpenAIAssistantAgent",
        "MultimodalWebSurfer",
        "FileSurfer",
        "VideoSurfer",
    }

    agents = {}
    for tree in trees:
        for node in ast.walk(tree):
            simple_function_call_assignment = parse_simple_function_call_assignment(
                node
            )
            if not simple_function_call_assignment:
                continue

            if simple_function_call_assignment.function_name not in KNOWN_AGENT_CLASSES:
                continue

            name = simple_function_call_assignment.resolve_arg_or_kwarg(0, "name")
            if not isinstance(name, str):
                continue

            model_client = simple_function_call_assignment.resolve_arg_or_kwarg(
                1, "model_client"
            )
            if not isinstance(model_client, str) or model_client not in model_clients:
                llm = ""
            else:
                llm = model_clients[model_client].model

            # For OpenAIAssistantAgent
            model = simple_function_call_assignment.kwargs.get("model")
            if not isinstance(model, str):
                model = ""

            instructions = simple_function_call_assignment.kwargs.get("instructions")
            if not isinstance(instructions, str):
                instructions = ""

            system_prompt = simple_function_call_assignment.kwargs.get("system_message")
            if not isinstance(system_prompt, str):
                system_prompt = ""

            tools_arg = simple_function_call_assignment.kwargs.get("tools", [])
            tools = []
            if isinstance(tools_arg, list):
                for tool_arg in tools_arg:
                    if not isinstance(tool_arg, str):
                        continue
                    if tool_arg in function_tools:
                        tools.append(function_tools[tool_arg])
                    if tool_arg in all_functions:
                        # If it's a function, we can create a tool for it
                        function_def = all_functions[tool_arg]
                        tools.append(
                            FunctionTool(
                                name=function_def.name,
                                description=function_def.description,
                            )
                        )

            handoffs = simple_function_call_assignment.kwargs.get("handoffs", [])
            if not isinstance(handoffs, list):
                handoffs = []
            handoffs = [handoff for handoff in handoffs if isinstance(handoff, str)]

            agents[simple_function_call_assignment.target] = Agent(
                name=name,
                tools=tools,
                llm=llm or model,
                system_prompt=system_prompt or instructions,
                handoffs=handoffs,
            )

    return agents


def find_teams(trees: list[ast.AST], agents: dict[str, Agent]) -> list[Team]:
    """
    Finds all Autogen teams created in the code.
    """
    KNOWN_TEAM_CLASSES = {
        "RoundRobinGroupChat": TeamType.ROUND_ROBIN_GROUP_CHAT,
        "SelectorGroupChat": TeamType.SELECTOR_GROUP_CHAT,
        "MagenticOneGroupChat": TeamType.MAGENTIC_ONE_GROUP_CHAT,
        "Swarm": TeamType.SWARM,
    }

    teams = []
    for tree in trees:
        for node in ast.walk(tree):
            simple_function_call_assignment = parse_simple_function_call_assignment(
                node
            )
            if not simple_function_call_assignment:
                continue

            if simple_function_call_assignment.function_name not in KNOWN_TEAM_CLASSES:
                continue

            participants = simple_function_call_assignment.resolve_arg_or_kwarg(
                0, "participants"
            )
            if not isinstance(participants, list):
                continue
            members = [
                agents[member]
                for member in participants
                if isinstance(member, str) and member in agents
            ]

            teams.append(
                Team(
                    type=KNOWN_TEAM_CLASSES[
                        simple_function_call_assignment.function_name
                    ],
                    members=members,
                )
            )

    return teams
