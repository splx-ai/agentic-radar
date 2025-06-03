import datetime
import os
import shlex
import time
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from pydantic import ValidationError
from typing_extensions import Annotated

from agentic_radar import __version__
from agentic_radar.analysis import (
    Analyzer,
    AutogenAgentChatAnalyzer,
    CrewAIAnalyzer,
    LangGraphAnalyzer,
    N8nAnalyzer,
    OpenAIAgentsAnalyzer,
)
from agentic_radar.graph import Agent
from agentic_radar.mapper import map_vulnerabilities
from agentic_radar.prompt_hardening.harden import harden_agent_prompts
from agentic_radar.prompt_hardening.pipeline import PromptHardeningPipeline
from agentic_radar.prompt_hardening.steps import OpenAIGeneratorStep, PIIProtectionStep
from agentic_radar.report import (
    EdgeDefinition,
    GraphDefinition,
    NodeDefinition,
    generate,
)
from agentic_radar.test import Test, load_tests
from agentic_radar.utils import sanitize_graph

load_dotenv()

app = typer.Typer()


class AgenticFramework(str, Enum):
    langgraph = "langgraph"
    crewai = "crewai"
    n8n = "n8n"
    openai_agents = "openai-agents"
    autogen = "autogen"


@app.callback(invoke_without_command=True)
def version_callback(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", is_eager=True),
    ] = None,
):
    if version:
        print(f"SplxAI Agentic Radar Version: {__version__}")
        raise typer.Exit()


@app.command("scan", help="Scan code for agentic workflows and generate a report")
def scan(
    framework: Annotated[
        AgenticFramework,
        typer.Argument(
            help="Framework to scan",
        ),
    ],
    input_directory: Annotated[
        str,
        typer.Option(
            "--input-dir",
            "-i",
            help="Path to the directory where all the code is",
            envvar="AGENTIC_RADAR_INPUT_DIRECTORY",
        ),
    ] = ".",
    output_file: Annotated[
        str,
        typer.Option(
            "--output-file",
            "-o",
            help="Where should the output report be stored",
            envvar="AGENTIC_RADAR_OUTPUT_FILE",
        ),
    ] = f"report_{datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')}.html",
    harden_prompts: Annotated[
        bool,
        typer.Option(
            "--harden-prompts",
            help="Harden detected system prompts. Requires OPENAI_API_KEY or AZURE_OPENAI_API_KEY. You can set it in .env file or as an environment variable.",
            is_flag=True,
            envvar="AGENTIC_RADAR_HARDEN_PROMPTS",
        ),
    ] = False,
):
    if not os.path.isdir(input_directory):
        print(f"Input directory '{input_directory}' does not exist.")
        raise typer.Exit(code=1)

    analyzer: Analyzer
    if framework == AgenticFramework.langgraph:
        analyzer = LangGraphAnalyzer()
    elif framework == AgenticFramework.crewai:
        analyzer = CrewAIAnalyzer()
    elif framework == AgenticFramework.n8n:
        analyzer = N8nAnalyzer()
    elif framework == AgenticFramework.openai_agents:
        analyzer = OpenAIAgentsAnalyzer()
    elif framework == AgenticFramework.autogen:
        analyzer = AutogenAgentChatAnalyzer()
    else:
        print(f"Unsupported framework: {framework}")
        raise typer.Exit(code=1)

    analyze_and_generate_report(
        framework=framework.value,
        analyzer=analyzer,
        input_directory=input_directory,
        output_file=output_file,
        harden_prompts=harden_prompts,
    )


def analyze_and_generate_report(
    framework: str,
    analyzer: Analyzer,
    input_directory: str,
    output_file: str,
    harden_prompts: bool,
):
    print(f"Analyzing {input_directory} for {framework} graphs")
    graph = analyzer.analyze(input_directory)

    if len(graph.nodes) <= 2:  # Only start and end nodes are present
        print(
            f"Agentic Radar didn't find any agentic workflow in input directory: {input_directory}"
        )
        raise typer.Exit(code=1)
    sanitize_graph(graph)

    print("Mapping vulnerabilities")
    map_vulnerabilities(graph)

    if harden_prompts:
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("AZURE_OPENAI_API_KEY"):
            print(
                "Hardening system prompts requires OPENAI_API_KEY or AZURE_OPENAI_API_KEY. "
                "You can set it in .env file or as an environment variable."
            )
            raise typer.Exit(code=1)
        print("Hardening system prompts")
        pipeline = PromptHardeningPipeline([OpenAIGeneratorStep(), PIIProtectionStep()])
        hardened_prompts = harden_agent_prompts(graph.agents, pipeline)
    else:
        hardened_prompts = {}

    pydot_graph = GraphDefinition(
        framework=framework,
        name=graph.name,
        nodes=[
            NodeDefinition.model_validate(n, from_attributes=True) for n in graph.nodes
        ],
        edges=[
            EdgeDefinition.model_validate(e, from_attributes=True) for e in graph.edges
        ],
        agents=[Agent.model_validate(a, from_attributes=True) for a in graph.agents],
        tools=[
            NodeDefinition.model_validate(t, from_attributes=True) for t in graph.tools
        ],
        hardened_prompts=hardened_prompts,
    )
    print("Generating report")
    generate(pydot_graph, output_file)
    print(f"Report {output_file} generated")


@app.command(
    "test",
    help="Test agents in an agentic workflow for various vulnerabilities. Requires OPENAI_API_KEY or AZURE_OPENAI_API_KEY set as an environment variable.",
)
def test(
    framework: Annotated[
        AgenticFramework,
        typer.Argument(
            help="Framework of the agentic workflow to test",
        ),
    ],
    entrypoint_script_with_args: Annotated[
        str,
        typer.Argument(
            help='Path to the entrypoint script which runs the agentic workflow, along with any arguments necessary to run it, eg. "myscript.py --arg1 value1 --arg2 value2"',
        ),
    ],
    config: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            "-c",
            help="Path to the YAML file containing the Agentic Radar Test configuration. If not provided, the default test suite will be used.",
            envvar="AGENTIC_RADAR_TEST_CONFIG_FILE",
        ),
    ] = None,
):
    split_args = shlex.split(entrypoint_script_with_args)
    entrypoint_script = split_args[0]
    extra_args = split_args[1:]
    if not os.path.isfile(entrypoint_script):
        print(f"Entrypoint script '{entrypoint_script}' does not exist.")
        raise typer.Exit(code=1)

    print(f"Testing {entrypoint_script} for {framework} agents")
    try:
        tests: list[Test] = load_tests(config_path=config)
    except (ValidationError, ValueError) as e:
        print(f"Error loading tests: {e}")
        raise typer.Exit(code=1)
    print(f"Loaded {len(tests)} tests")
    if framework == AgenticFramework.openai_agents:
        try:
            import agents  # noqa: F401
        except ImportError:
            print(
                "The OpenAI Agents library is not installed. Please install it using 'pip install openai-agents'."
            )
            raise typer.Exit(code=1)

        from agentic_radar.test import OpenAIAgentsLauncher

        launcher = OpenAIAgentsLauncher(entrypoint_script, extra_args, tests)
    else:
        print(f"Unsupported framework: {framework}")
        raise typer.Exit(code=1)

    launcher.launch()


if __name__ == "__main__":
    app()
