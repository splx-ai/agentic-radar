from typing import Optional

import typer
from typing_extensions import Annotated

from agentic_scanner.analysis.langgraph.analyze import LangGraphAnalyzer
from agentic_scanner.visualization.parse import (
    EdgeDefinition,
    GraphDefinition,
    NodeDefinition,
    from_definition,
)

app = typer.Typer()

from agentic_scanner import __version__


def version_callback(value: bool):
    if value:
        print(f"SplxAI Agentic Scanner Version: {__version__}")
        raise typer.Exit()


@app.command()
def main(
    input_directory: Annotated[
        str,
        typer.Option(
            "--input-dir",
            "-i",
            help="Path to the directory where all the code is",
            envvar="AGENTIC_SCANNER_INPUT_DIRECTORY",
        ),
    ] = ".",
    output_file: Annotated[
        str,
        typer.Option(
            "--output-file",
            "-o",
            help="Where should the output report be stored",
            envvar="AGENTIC_SCANNER_OUTPUT_FILE",
        ),
    ] = "out.svg",
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    analyzer = LangGraphAnalyzer()
    graph = analyzer.analyze(input_directory)
    pydot_graph = GraphDefinition(
        nodes=[
            NodeDefinition.model_validate(n, from_attributes=True) for n in graph.nodes
        ],
        edges=[
            EdgeDefinition.model_validate(e, from_attributes=True) for e in graph.edges
        ],
    )
    from_definition(pydot_graph).generate(output_file)


if __name__ == "__main__":
    app()
