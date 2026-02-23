"""
Git utility functions for subprocess-based git operations.

Provides wrappers for common git operations with proper error handling.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def is_git_repo() -> bool:
    """
    Check if the current directory is inside a git repository.

    Returns:
        bool: True if inside a git repo, False otherwise.
    """
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_staged_files() -> list[str]:
    """
    Get list of staged files.

    Returns:
        list[str]: List of file paths that are staged for commit.

    Raises:
        RuntimeError: If git command fails.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [f for f in result.stdout.strip().split("\n") if f]
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get staged files: {e.stderr}")


def get_staged_diff() -> str:
    """
    Get the diff of staged changes.

    Returns:
        str: The unified diff of staged changes.

    Raises:
        RuntimeError: If git command fails.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get staged diff: {e.stderr}")


def commit_with_message(title: str, body: str) -> bool:
    """
    Commit with a title and body following Conventional Commits format.

    Args:
        title: The commit title (e.g., "fix: correct login validation").
        body: The commit body (multiline explanation).

    Returns:
        bool: True if commit succeeded, False otherwise.
    """
    try:
        subprocess.run(
            ["git", "commit", "-m", title, "-m", body],
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        return False


def passthrough_git_command() -> int:
    """
    Pass all arguments directly to git and stream output.

    This function extracts all command-line arguments after the program name
    and passes them to git, preserving exit codes and streaming output.

    Returns:
        int: The exit code from the git command.
    """
    try:
        result = subprocess.run(["git"] + sys.argv[1:])
        return result.returncode
    except FileNotFoundError:
        print(
            "Error: git is not installed or not in PATH. "
            "Please install git to use lit.",
            file=sys.stderr,
        )
        return 1


def get_git_root() -> Optional[Path]:
    """
    Get the root directory of the git repository.

    Returns:
        Optional[Path]: Path to git root directory, or None if not in a git repo.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        return None
