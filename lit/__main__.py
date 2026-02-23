"""
Entry point for the lit CLI tool.

This module provides the main() function that Typer calls when the CLI is invoked.
It handles asyncio event loop setup and delegates to the CLI router.

Usage Examples:
    # Basic passthrough to git
    $ lit status                          # Shows git status
    $ lit add file.py                     # Stages file.py
    $ lit push -u origin main             # Pushes to remote

    # Special commit flow with translation
    $ lit commit -m "login ka bug fix"    # Hinglish message
    # → Translates to English via Lingo.dev
    # → Analyzes diff
    # → Generates Conventional Commit
    # → Shows preview and asks for confirmation
    # → Commits

    # Other git commands work as-is
    $ lit log --oneline                   # Shows commit log
    $ lit merge feature-branch            # Merges branch
    $ lit checkout -b new-feature         # Creates new branch
"""

import sys

from lit.cli import app


def main() -> None:
    """
    Main entry point for the lit CLI.

    Sets up the Typer app and delegates all routing.
    """
    app()


if __name__ == "__main__":
    main()
