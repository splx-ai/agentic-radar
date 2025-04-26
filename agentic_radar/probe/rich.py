from rich.console import Console
from rich.table import Table
from rich.text import Text

from .probe import ProbeResult

console = Console()


def display_probe_results(results: list[ProbeResult]) -> None:
    table = Table(title="Probe Results", show_lines=True)

    table.add_column("Agent Name", justify="left", style="cyan")
    table.add_column("Probe Name", justify="left", style="magenta")
    table.add_column("Input", justify="left", style="yellow")
    table.add_column("Output", justify="left", style="yellow")
    table.add_column("Test Passed", justify="left")
    table.add_column("Explanation", justify="left")

    for result in results:
        status = "[green]PASSED[/green]" if result.test_passed else "[red]FAILED[/red]"
        table.add_row(
            result.agent_name,
            result.probe_name,
            Text(result.input, overflow="fold"),
            Text(result.output, overflow="fold"),
            status,
            Text(
                result.explanation,
                overflow="fold",
                style="green" if result.test_passed else "red",
            ),
        )

    console.print(table)
