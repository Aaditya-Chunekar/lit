"""
Orchestration logic for the commit flow.

Handles the full lifecycle of a special commit:
1. Validation (staged files, git repo)
2. Diff extraction
3. Lingo SDK translation with spinner
4. Preview and confirmation
5. Final commit execution
"""

import asyncio
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
import questionary

from lit.git_utils import (
    commit_with_message,
    get_staged_diff,
    get_staged_files,
    is_git_repo,
)
from lit.lingo_utils import (
    ConventionalCommit,
    fallback_generate_commit,
    translate_commit_message,
)

console = Console()


class CommitFlowError(Exception):
    """Custom exception for commit flow errors."""

    pass


async def run_commit_flow(raw_message: str) -> bool:
    """
    Execute the full commit flow with translation and verification.

    This is the core orchestrator that:
    1. Validates preconditions (git repo, staged files)
    2. Extracts staged diff
    3. Calls Lingo SDK with spinner
    4. Shows preview and asks for confirmation
    5. Performs final commit

    Args:
        raw_message: The raw commit message from user input.

    Returns:
        bool: True if commit succeeded, False if cancelled.

    Raises:
        CommitFlowError: If any critical step fails.
    """
    try:
        # Step 1: Check if inside a git repo
        if not is_git_repo():
            console.print(
                "[red]Error:[/red] Not inside a git repository.",
                style="bold red",
            )
            raise CommitFlowError("Not in a git repository")

        # Step 2: Check if files are staged
        staged_files = get_staged_files()
        if not staged_files:
            console.print(
                "[red]No staged files.[/red] Run [cyan]git add[/cyan] first.",
                style="bold red",
            )
            raise CommitFlowError("No staged files")

        # Step 3: Extract staged diff
        staged_diff = get_staged_diff()
        if not staged_diff:
            console.print(
                "[yellow]Warning:[/yellow] Staged changes are empty.",
                style="bold yellow",
            )

        # Step 4: Translate using Lingo with spinner
        console.print()
        commit = await _translate_with_spinner(raw_message, staged_diff)

        # Step 5: Show preview
        _show_commit_preview(commit)

        # Step 6: Ask for confirmation
        action = questionary.select(
            "Commit with this message?",
            choices=["✓ Accept", "✏ Edit manually", "✗ Cancel"],
            qmark="",
            pointer="→",
        ).ask()

        if action is None or action.startswith("✗"):
            console.print("[yellow]Commit cancelled.[/yellow]")
            return False

        if action.startswith("✏"):
            # Allow manual edit
            commit = await _edit_commit_manually(commit)

        # Step 7: Perform final commit
        title, body = commit.format_message()
        if commit_with_message(title, body):
            console.print()
            console.print(
                "[green]✓ Commit successful![/green]",
                style="bold green",
            )
            console.print(f"[cyan]{title}[/cyan]")
            return True
        else:
            console.print(
                "[red]✗ Commit failed. Check git status.[/red]",
                style="bold red",
            )
            return False

    except CommitFlowError as e:
        console.print(f"[red]Commit flow error:[/red] {e}", style="bold red")
        return False
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        return False


async def _translate_with_spinner(
    raw_message: str, staged_diff: str
) -> ConventionalCommit:
    """
    Translate the commit message with a spinner showing progress.

    Falls back to heuristic generation if SDK fails.

    Args:
        raw_message: The raw user message.
        staged_diff: The git diff.

    Returns:
        ConventionalCommit: The generated commit.
    """
    with console.status(
        "[cyan]⟳[/cyan] Translating and analyzing via Lingo.dev...",
        spinner="dots",
    ) as status:
        try:
            commit = await translate_commit_message(raw_message, staged_diff)
            if commit:
                return commit
            else:
                console.print(
                    "[yellow]Warning:[/yellow] Failed to parse SDK response. "
                    "Using fallback.",
                    style="bold yellow",
                )
                return fallback_generate_commit(raw_message, staged_diff)

        except (RuntimeError, ValueError) as e:
            console.print()
            console.print(
                f"[yellow]Translation failed:[/yellow] {e}",
                style="bold yellow",
            )
            console.print("[yellow]Using heuristic generation as fallback...[/yellow]")
            return fallback_generate_commit(raw_message, staged_diff)


def _show_commit_preview(commit: ConventionalCommit) -> None:
    """
    Display a clean preview of the generated commit.

    Args:
        commit: The commit to preview.
    """
    title, body = commit.format_message()
    preview_text = f"[bold cyan]{title}[/bold cyan]\n\n{body}"

    panel = Panel(
        preview_text,
        title="[bold]Commit Preview[/bold]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


async def _edit_commit_manually(commit: ConventionalCommit) -> ConventionalCommit:
    """
    Allow user to manually edit the title and body.

    Args:
        commit: The original commit to edit.

    Returns:
        ConventionalCommit: The edited commit.
    """
    console.print()
    new_title = questionary.text(
        "Edit title:",
        default=commit.title,
    ).ask()

    new_body = questionary.text(
        "Edit body:",
        default=commit.body,
        multiline=True,
    ).ask()

    if new_title and new_body:
        return ConventionalCommit(type=commit.type, title=new_title, body=new_body)
    else:
        console.print("[yellow]Edit cancelled. Using original.[/yellow]")
        return commit
