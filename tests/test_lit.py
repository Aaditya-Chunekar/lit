"""
Example test suite for lit CLI.

This demonstrates how to test the lit CLI components.
Run with: pytest tests/test_lit.py -v
"""

import pytest
from lit.lingo_utils import (
    ConventionalCommit,
    parse_lingo_response,
    validate_conventional_commit_type,
    validate_conventional_commit_title,
    fallback_generate_commit,
)


class TestConventionalCommitValidation:
    """Tests for Conventional Commit validation."""

    def test_valid_commit_type(self):
        """Test valid commit types."""
        valid_types = ["feat", "fix", "refactor", "docs", "chore", "test", "perf"]
        for commit_type in valid_types:
            assert validate_conventional_commit_type(commit_type)

    def test_invalid_commit_type(self):
        """Test invalid commit types."""
        invalid_types = ["feature", "bug", "update", "wip", "hotfix"]
        for commit_type in invalid_types:
            assert not validate_conventional_commit_type(commit_type)

    def test_commit_title_under_72_chars(self):
        """Test title under 72 characters is valid."""
        title = "add validation checks to login"
        assert validate_conventional_commit_title(title)

    def test_commit_title_over_72_chars(self):
        """Test title over 72 characters is invalid."""
        title = "this is a very long commit title that exceeds 72 characters and should fail"
        assert not validate_conventional_commit_title(title)

    def test_commit_title_with_trailing_period(self):
        """Test title with trailing period is invalid."""
        title = "add validation checks."
        assert not validate_conventional_commit_title(title)


class TestJsonParsing:
    """Tests for Lingo SDK response parsing."""

    def test_parse_valid_json_response(self):
        """Test parsing valid Lingo response."""
        response = """
        {
            "type": "fix",
            "title": "correct login validation logic",
            "body": "add required field checks\\nresolve null pointer issue"
        }
        """
        commit = parse_lingo_response(response)
        assert commit is not None
        assert commit.type == "fix"
        assert commit.title == "correct login validation logic"

    def test_parse_json_with_surrounding_text(self):
        """Test parsing JSON embedded in surrounding text."""
        response = """
        Here's the commit:
        
        {
            "type": "feat",
            "title": "add oauth integration",
            "body": "implement oauth 2.0 flow"
        }
        
        Done!
        """
        commit = parse_lingo_response(response)
        assert commit is not None
        assert commit.type == "feat"

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON returns None."""
        response = "not valid json"
        commit = parse_lingo_response(response)
        assert commit is None

    def test_parse_json_missing_fields(self):
        """Test parsing JSON with missing fields returns None."""
        response = '{"type": "fix", "title": "test"}'  # Missing body
        commit = parse_lingo_response(response)
        assert commit is None

    def test_parse_json_invalid_type(self):
        """Test parsing JSON with invalid type returns None."""
        response = """
        {
            "type": "invalid",
            "title": "test",
            "body": "test body"
        }
        """
        commit = parse_lingo_response(response)
        assert commit is None


class TestFallbackGeneration:
    """Tests for fallback commit generation."""

    def test_fallback_detects_fix_type(self):
        """Test fallback detects 'fix' keyword."""
        message = "fixed the login bug"
        diff = ""
        commit = fallback_generate_commit(message, diff)
        assert commit.type == "fix"

    def test_fallback_detects_feat_type(self):
        """Test fallback detects 'feat' keyword or new files."""
        message = "added new authentication module"
        diff = "new file: auth.py"
        commit = fallback_generate_commit(message, diff)
        assert commit.type == "feat"

    def test_fallback_detects_chore_type(self):
        """Test fallback detects formatting changes."""
        message = "update code formatting"
        diff = "whitespace formatting changes"
        commit = fallback_generate_commit(message, diff)
        assert commit.type == "chore"

    def test_fallback_default_refactor(self):
        """Test fallback defaults to refactor."""
        message = "some generic change"
        diff = ""
        commit = fallback_generate_commit(message, diff)
        assert commit.type == "refactor"


class TestConventionalCommitFormatting:
    """Tests for Conventional Commit formatting."""

    def test_format_message_with_type_and_title(self):
        """Test formatted message includes type and title."""
        commit = ConventionalCommit(
            type="fix",
            title="correct validation logic",
            body="detailed explanation",
        )
        title, body = commit.format_message()
        assert title == "fix: correct validation logic"
        assert body == "detailed explanation"

    def test_format_preserves_multiline_body(self):
        """Test formatted message preserves multiline body."""
        body_text = "line 1\nline 2\nline 3"
        commit = ConventionalCommit(
            type="feat", title="add feature", body=body_text
        )
        _, body = commit.format_message()
        assert body == body_text


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_message(self):
        """Test fallback handles empty message."""
        commit = fallback_generate_commit("", "")
        assert commit is not None
        assert commit.type in ["feat", "fix", "refactor", "docs", "chore", "test", "perf"]

    def test_very_long_message(self):
        """Test fallback truncates very long message."""
        long_message = "a" * 200
        commit = fallback_generate_commit(long_message, "")
        assert len(commit.title) <= 72

    def test_unicode_in_message(self):
        """Test handling of unicode characters."""
        message = "login का bug fix किया"
        commit = fallback_generate_commit(message, "")
        assert commit.title is not None
        assert len(commit.title) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
