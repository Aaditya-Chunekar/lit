"""
Entry point for the lit CLI tool.

This module provides the main() function that is called when the CLI is invoked.

Usage Examples:
    $ lit status                          # Shows git status
    $ lit add file.py                     # Stages file.py
    $ lit push -u origin main             # Pushes to remote
    $ lit commit -m "login ka bug fix"    # Smart commit with translation
    $ lit log --oneline                   # Shows commit log
"""

from lit.cli import main


if __name__ == "__main__":
    main()
