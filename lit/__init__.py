"""
lit: Type how you think, commit effortlessly.

A production-ready Python CLI wrapper over git with AI-powered Conventional Commits.

When you run 'lit commit', it:
1. Detects your commit message language (supports mixed languages like Hinglish)
2. Analyzes the staged diff
3. Generates a proper Conventional Commit via Lingo.dev
4. Shows a preview and asks for confirmation
5. Commits with the generated message

All other git commands pass through directly.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from lit.cli import app

__all__ = ["app"]
