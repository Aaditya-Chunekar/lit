"""
Typer CLI application for the lit command.

Routes commands:
- lit commit → special flow with translation and Conventional Commits
- All other commands → passthrough to git
"""

import asyncio
import sys
from typing import Optional

import typer
from rich.console import Console

from lit.commit_flow import run_commit_flow
from lit.git_utils import passthrough_git_command

app = typer.Typer(
    name="lit",
    help="Type how you think, commit effortlessly. Git wrapper with AI-powered commits.",
    no_args_is_help=False,
    invoke_without_command=True,
)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
) -> None:
    """
    Main entry point for the lit CLI.

    Routes to either:
    - commit flow if 'commit' is the first argument
    - git passthrough for all other commands
    """
    # Get raw arguments
    args = sys.argv[1:]

    if not args:
        # No arguments: show help
        console.print(app.get_help(ctx))
        raise typer.Exit(0)

    # Check if the first argument is 'commit'
    if args[0] == "commit":
        # Handle special commit flow
        _handle_commit(args)
    else:
        # Passthrough to git
        exit_code = passthrough_git_command()
        raise typer.Exit(exit_code)


def _handle_commit(args: list[str]) -> None:
    """
    Handle the special 'lit commit' flow.

    Extracts the message from:
    - lit commit -m "message"
    - lit commit -m "message" --amend
    - Etc.

    Args:
        args: The command arguments (starting with 'commit').
    """
    # Extract the message from -m flag
    message = None
    has_amend = "--amend" in args or "-a" in args

    for i, arg in enumerate(args):
        if arg == "-m" and i + 1 < len(args):
            message = args[i + 1]
            break

    if not message:
        console.print(
            "[red]Error:[/red] Commit requires a message. Use: [cyan]lit commit -m \"message\"[/cyan]",
            style="bold red",
        )
        raise typer.Exit(1)

    # Run the async commit flow
    try:
        success = asyncio.run(run_commit_flow(message))
        exit_code = 0 if success else 1
        raise typer.Exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
