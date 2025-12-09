"""Main CLI entry point for LCR application."""

import typer
from rich.console import Console

app = typer.Typer(
    name="lcr",
    help="LeetCode Repetition CLI - Track and schedule LeetCode problem reviews",
    add_completion=False,
)

console = Console()


@app.command()
def version() -> None:
    """Display version information."""
    console.print("[bold blue]LCR[/bold blue] version [green]0.1.0[/green]")
    console.print("LeetCode Repetition CLI - Spaced repetition for coding practice")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """LeetCode Repetition (LCR) CLI.
    
    A tool for tracking and scheduling LeetCode problem reviews
    using spaced repetition algorithms.
    """
    if ctx.invoked_subcommand is None:
        console.print("[yellow]Welcome to LCR![/yellow]")
        console.print("\nUse [bold]lcr --help[/bold] to see available commands.")
        console.print("\n[dim]Commands to be implemented:[/dim]")
        console.print("  • [cyan]lcr add[/cyan] - Register a problem for review")
        console.print("  • [cyan]lcr checkin[/cyan] - Mark a review as completed")
        console.print("  • [cyan]lcr list[/cyan] - Show today's pending reviews")
        console.print("  • [cyan]lcr review[/cyan] - View progress and history")
        console.print("  • [cyan]lcr start/end[/cyan] - Track problem-solving time")
        console.print("\n[bold green]Phase 1: Project Setup - Complete![/bold green]")


if __name__ == "__main__":
    app()
