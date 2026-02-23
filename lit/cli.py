"""
CLI router for the lit command.

Routes commands:
- lit commit → special flow with translation and Conventional Commits
- All other commands → passthrough to git
"""

import asyncio
import sys
from rich.console import Console

from lit.commit_flow import run_commit_flow
from lit.git_utils import passthrough_git_command

console = Console()


def main() -> None:
    """
    Main entry point for the lit CLI.

    Routes to either:
    - commit flow if 'commit' is the first argument
    - git passthrough for all other commands
    """
    args = sys.argv[1:]

    if not args or args[0] in ["--help", "-h", "help"]:
        # No arguments or help requested: show help
        console.print("[cyan]lit[/cyan] - Type how you think, commit effortlessly.")
        console.print()
        console.print("Usage: [cyan]lit <git-command>[/cyan] or [cyan]lit commit -m \"message\"[/cyan]")
        console.print()
        console.print("Examples:")
        console.print("  [cyan]lit status[/cyan]              # Git passthrough")
        console.print("  [cyan]lit push origin main[/cyan]    # Git passthrough")
        console.print("  [cyan]lit commit -m \"message\"[/cyan] # AI-powered commit")
        sys.exit(0)

    # Check if the first argument is 'commit'
    if args[0] == "commit":
        _handle_commit(args)
    else:
        # Passthrough to git
        exit_code = passthrough_git_command()
        sys.exit(exit_code)


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

    for i, arg in enumerate(args):
        if arg == "-m" and i + 1 < len(args):
            message = args[i + 1]
            break

    if not message:
        console.print(
            "[red]Error:[/red] Commit requires a message. Use: [cyan]lit commit -m \"message\"[/cyan]",
            style="bold red",
        )
        sys.exit(1)

    # Run the async commit flow
    try:
        success = asyncio.run(run_commit_flow(message))
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        sys.exit(1)
