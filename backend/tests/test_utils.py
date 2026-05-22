"""
Tests for core/utils.py

Validates:
- sanitize_prompt(): control chars stripped, \t\n\r preserved, truncation, edge cases
"""

import pytest
from core.utils import sanitize_prompt


class TestSanitizePrompt:
    """sanitize_prompt() — input sanitization for AI prompts."""

    def test_strips_control_characters(self):
        """Control characters (\\x00-\\x1f except \\t\\n\\r) MUST be stripped."""
        text = "hello\x00world\x01test\x1Fend"
        result = sanitize_prompt(text)
        assert result == "helloworldtestend"
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x1F" not in result

    def test_preserves_tab_newline_carriage_return(self):
        """Tab, newline, and carriage return MUST be preserved."""
        text = "line1\nline2\tindented\r\nline3"
        result = sanitize_prompt(text)
        assert result == "line1\nline2\tindented\r\nline3"
        assert "\t" in result
        assert "\n" in result
        assert "\r" in result

    def test_strips_mixed_control_and_valid_chars(self):
        """Mixture of control chars and valid chars — only controls stripped."""
        text = "a\x00b\nc\x01d\te\x1Ff"
        result = sanitize_prompt(text)
        assert result == "ab\ncd\tef"

    def test_truncates_at_max_len(self):
        """Text exceeding max_len MUST be truncated to max_len characters."""
        text = "a" * 3000
        result = sanitize_prompt(text, max_len=2000)
        assert len(result) == 2000
        assert result == "a" * 2000

    def test_truncates_at_custom_max_len(self):
        """Custom max_len parameter MUST be respected."""
        text = "x" * 500
        result = sanitize_prompt(text, max_len=100)
        assert len(result) == 100
        assert result == "x" * 100

    def test_short_text_not_truncated(self):
        """Text below max_len MUST NOT be truncated."""
        text = "short text"
        result = sanitize_prompt(text, max_len=2000)
        assert result == "short text"
        assert len(result) == 10

    def test_control_chars_stripped_before_truncation(self):
        """Control chars must be stripped BEFORE truncation."""
        text = "hello\x00\x01\x02" + "x" * 2000
        result = sanitize_prompt(text, max_len=2000)
        # 5 chars "hello" + 2000 "x" = 2005 chars after stripping 3 controls
        # But after stripping 3 controls, we have 2005 chars → truncated to 2000
        assert len(result) == 2000
        assert result.startswith("hello")

    def test_empty_string(self):
        """Empty string MUST return empty string."""
        assert sanitize_prompt("") == ""

    def test_only_control_chars(self):
        """String consisting only of control chars MUST return empty string."""
        text = "\x00\x01\x02\x1E\x1F"
        result = sanitize_prompt(text)
        assert result == ""

    def test_none_input(self):
        """None input MUST return empty string."""
        assert sanitize_prompt(None) == ""

    def test_default_max_len_is_2000(self):
        """Default max_len parameter MUST be 2000."""
        import inspect
        sig = inspect.signature(sanitize_prompt)
        assert sig.parameters["max_len"].default == 2000
