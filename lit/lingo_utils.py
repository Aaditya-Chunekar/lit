"""
Lingo SDK integration for commit message translation and Conventional Commit generation.

Handles async communication with Lingo.dev to translate user messages
and analyze diffs for generating properly formatted Conventional Commits.
"""

import asyncio
import json
import os
import re
from dataclasses import dataclass
from typing import Optional, Tuple

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from lingodotdev import LingoDotDevEngine
except ImportError:
    LingoDotDevEngine = None  # type: ignore


@dataclass
class ConventionalCommit:
    """Represents a Conventional Commit with type, title, and body."""

    type: str
    title: str
    body: str

    def format_message(self) -> Tuple[str, str]:
        """
        Format the commit as (title, body) for git commit.

        Returns:
            Tuple[str, str]: (formatted_title, formatted_body)
        """
        formatted_title = f"{self.type}: {self.title}"
        return formatted_title, self.body


def validate_conventional_commit_type(commit_type: str) -> bool:
    """
    Validate if the commit type is one of the allowed Conventional Commit types.

    Args:
        commit_type: The type to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    allowed_types = {"feat", "fix", "refactor", "docs", "chore", "test", "perf"}
    return commit_type.lower() in allowed_types


def validate_conventional_commit_title(title: str) -> bool:
    """
    Validate commit title constraints.

    Args:
        title: The title to validate.

    Returns:
        bool: True if valid (under 72 chars, no trailing period), False otherwise.
    """
    if len(title) > 72:
        return False
    if title.endswith("."):
        return False
    return True


def parse_lingo_response(response: str) -> Optional[ConventionalCommit]:
    """
    Parse the Lingo SDK response and extract Conventional Commit data.

    The response should contain a JSON object with:
        {
            "type": "fix|feat|refactor|docs|chore|test|perf",
            "title": "short description",
            "body": "detailed explanation"
        }

    Args:
        response: The raw response string from Lingo SDK.

    Returns:
        Optional[ConventionalCommit]: Parsed commit, or None if parsing fails.
    """
    try:
        # Try to extract JSON from the response (may have surrounding text)
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if not json_match:
            return None

        json_str = json_match.group(0)
        data = json.loads(json_str)

        # Validate required fields
        if not all(k in data for k in ["type", "title", "body"]):
            return None

        commit_type = data.get("type", "").lower()
        title = data.get("title", "").strip()
        body = data.get("body", "").strip()

        # Validate constraints
        if not validate_conventional_commit_type(commit_type):
            return None
        if not validate_conventional_commit_title(title):
            return None
        if not body:
            return None

        return ConventionalCommit(type=commit_type, title=title, body=body)
    except json.JSONDecodeError:
        return None
    except (KeyError, AttributeError, TypeError):
        return None


async def translate_commit_message(
    raw_message: str, staged_diff: str
) -> Optional[ConventionalCommit]:
    """
    Translate a raw commit message and diff to a Conventional Commit using Lingo SDK.

    This function handles:
    - Mixed language detection (e.g., Hinglish)
    - Translation to English
    - Diff analysis
    - JSON generation and parsing

    Args:
        raw_message: The raw user-provided commit message.
        staged_diff: The git diff of staged changes.

    Returns:
        Optional[ConventionalCommit]: The generated commit, or None on failure.

    Raises:
        RuntimeError: If LINGODOTDEV_API_KEY is missing or SDK call fails.
        ValueError: If SDK parameters are invalid.
    """
    api_key = os.environ.get("LINGODOTDEV_API_KEY")
    if not api_key:
        raise RuntimeError(
            "LINGODOTDEV_API_KEY environment variable is not set. "
            "Please set it to use the commit translation feature."
        )

    if LingoDotDevEngine is None:
        raise RuntimeError(
            "lingodotdev package is not installed. "
            "Install it with: pip install lingodotdev"
        )

    # System instruction embedded in the content
    system_instruction = (
        "Detect the source language. It may be a mixed colloquial language like "
        "Hinglish (Hindi + English). Translate the intent to standard English. "
        "Analyze the provided git diff. Generate a Conventional Commit in JSON format:\n\n"
        "{\n"
        '  "type": one of [feat, fix, refactor, docs, chore, test, perf],\n'
        '  "title": short description under 72 characters,\n'
        '  "body": concise explanation of what changed and why\n'
        "}\n\n"
        "Return ONLY valid JSON, no additional text."
    )

    # Prepare content to be translated
    content = {
        "instruction": system_instruction,
        "raw_message": raw_message,
        "diff": staged_diff,
    }

    try:
        async with LingoDotDevEngine({"api_key": api_key}) as engine:
            result = await engine.localize_object(
                content,
                {
                    "source_locale": None,
                    "target_locale": "en",
                    "fast": False,
                },
            )

            # Extract the translated content
            if hasattr(result, "translated"):
                translated_str = result.translated
            elif isinstance(result, str):
                translated_str = result
            elif isinstance(result, dict):
                translated_str = result.get("translated", str(result))
            else:
                translated_str = str(result)

            # Parse the response
            commit = parse_lingo_response(translated_str)
            return commit

    except ValueError as e:
        raise ValueError(f"Invalid parameters for Lingo SDK: {e}") from e
    except RuntimeError as e:
        raise RuntimeError(f"Lingo SDK error (network/API issue): {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error during translation: {e}") from e


def fallback_generate_commit(
    raw_message: str, staged_diff: str
) -> ConventionalCommit:
    """
    Fallback heuristic to generate a Conventional Commit if SDK fails.

    Uses simple keyword matching on the message and diff:
    - If "fix" keywords present → type = fix
    - If new files added → feat
    - If only formatting changes → chore
    - Default → refactor

    Args:
        raw_message: The raw user-provided message.
        staged_diff: The git diff of staged changes.

    Returns:
        ConventionalCommit: A best-effort generated commit.
    """
    message_lower = raw_message.lower()
    diff_lower = staged_diff.lower()

    # Detect type based on keywords
    if any(
        keyword in message_lower
        for keyword in ["fix", "bug", "issue", "correct", "resolve"]
    ):
        commit_type = "fix"
    elif any(keyword in message_lower for keyword in ["feat", "new", "add", "feature"]):
        commit_type = "feat"
    elif "new file:" in diff_lower:
        commit_type = "feat"
    elif all(
        keyword in diff_lower for keyword in ["whitespace", "formatting", "style"]
    ):
        commit_type = "chore"
    else:
        commit_type = "refactor"

    # Create a basic title from the message
    title = raw_message[:70] if len(raw_message) <= 70 else raw_message[:67] + "..."
    # Remove any type prefix if user included it
    if ":" in title:
        title = title.split(":", 1)[-1].strip()

    body = f"Original message: {raw_message}"

    return ConventionalCommit(type=commit_type, title=title, body=body)
