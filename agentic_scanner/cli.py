from typing import Optional

import typer
from typing_extensions import Annotated

app = typer.Typer()

from agentic_scanner import __version__
from agentic_scanner.visualization import from_json


def version_callback(value: bool):
    if value:
        print(f"SplxAI Agentic Scanner Version: {__version__}")
        raise typer.Exit()


@app.command()
def main(
    definition_file: Annotated[
        str,
        typer.Option(
            "--definition-file",
            "-f",
            help="Path to the file where the graph is defined",
            envvar="AGENTIC_SCANNER_DEFINITION_FILE",
        ),
    ],
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
    # TODO: call analysis, generate graph and write it to the output file
    # from_json().generate(output_file)
    pass


if __name__ == "__main__":
    app()
