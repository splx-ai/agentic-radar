from rich.console import Console
from rich.table import Table
from rich.text import Text

from .test import TestResult

console = Console()


def display_test_results(results: list[TestResult]) -> None:
    table = Table(title="Test Results", show_lines=True)

    table.add_column("Agent Name", justify="left", style="cyan")
    table.add_column("Test Name", justify="left", style="magenta")
    table.add_column("Input", justify="left", style="yellow")
    table.add_column("Output", justify="left", style="yellow")
    table.add_column("Test Passed", justify="left")
    table.add_column("Explanation", justify="left")

    for result in results:
        status = "[green]PASSED[/green]" if result.test_passed else "[red]FAILED[/red]"
        table.add_row(
            result.agent_name,
            result.test_name,
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
