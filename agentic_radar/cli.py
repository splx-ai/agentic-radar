import datetime
import os
import time
from typing import Optional

import typer
from pydantic import BaseModel
from typing_extensions import Annotated

from agentic_radar import __version__
from agentic_radar.analysis import (
    Analyzer,
    CrewAIAnalyzer,
    LangGraphAnalyzer,
    N8nAnalyzer,
    OpenAIAgentsAnalyzer,
)
from agentic_radar.graph import Agent
from agentic_radar.mapper import map_vulnerabilities
from agentic_radar.report import (
    EdgeDefinition,
    GraphDefinition,
    NodeDefinition,
    generate,
)
from agentic_radar.utils import sanitize_graph


class Args(BaseModel):
    input_directory: str
    output_file: str
    version: Optional[bool]


app = typer.Typer()
args: Args


def version_callback(value: bool):
    if value:
        print(f"SplxAI Agentic Radar Version: {__version__}")
        raise typer.Exit()


@app.callback()
def _main(
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
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    global args

    if not os.path.isdir(input_directory):
        print(f"Input directory '{input_directory}' does not exist.")
        raise typer.Exit(code=1)

    args = Args(
        input_directory=input_directory, output_file=output_file, version=version
    )


def analyze_and_generate_report(framework: str, analyzer: Analyzer):
    print(f"Analyzing {args.input_directory} for {framework} graphs")
    result = analyzer.analyze(args.input_directory)

    # Handle both single GraphDefinition and list of GraphDefinitions
    graphs = result if isinstance(result, list) else [result]

    if not graphs:
        print(
            f"Agentic Radar didn't find any agentic workflow in input directory: {args.input_directory}"
        )
        raise typer.Exit(code=1)

    for i, graph in enumerate(graphs):
        if len(graph.nodes) <= 2:  # Only start and end nodes are present
            print(f"Skipping workflow '{graph.name}' as it doesn't contain any agentic nodes")
            continue

        sanitize_graph(graph)

        print(f"Mapping vulnerabilities for workflow '{graph.name}'")
        map_vulnerabilities(graph)
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
        )

        # Generate a unique output file name for each workflow
        if len(graphs) > 1:
            base_name, ext = os.path.splitext(args.output_file)
            # Sanitize workflow name for use in filename
            safe_name = "".join(c if c.isalnum() else "_" for c in graph.name)
            output_file = f"{base_name}_{safe_name}{ext}"
        else:
            output_file = args.output_file

        print(f"Generating report for workflow '{graph.name}'")
        generate(pydot_graph, output_file)
        print(f"Report {output_file} generated")


@app.command("langgraph", help="Scan code written with LangGraph")
def langgraph():
    analyze_and_generate_report("LangGraph", LangGraphAnalyzer())


@app.command("crewai", help="Scan code written with CrewAI")
def crewai():
    analyze_and_generate_report("CrewAI", CrewAIAnalyzer())


@app.command("n8n", help="Scan a n8n workflow configuration JSON")
def n8n(
    connected_only: Annotated[
        bool,
        typer.Option(
            "--connected-only",
            help="Only generate reports for workflows with connected nodes",
        ),
    ] = False,
    langchain_only: Annotated[
        bool,
        typer.Option(
            "--langchain-only",
            help="Only generate reports for workflows that contain LangChain nodes",
        ),
    ] = False,
):
    print(f"Connected-only mode: {'Enabled' if connected_only else 'Disabled'}")
    print(f"LangChain-only mode: {'Enabled' if langchain_only else 'Disabled'}")
    analyze_and_generate_report("n8n", N8nAnalyzer(connected_only=connected_only, langchain_only=langchain_only))


@app.command("openai-agents", help="Scan code written with OpenAI Agents SDK")
def openai_agents():
    analyze_and_generate_report("openai-agents", OpenAIAgentsAnalyzer())


if __name__ == "__main__":
    app()
