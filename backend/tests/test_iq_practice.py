"""Tests for IQ Practice engine."""

import pytest
from core.iq_practice import evaluate_attempt, calculate_staircase


class TestEvaluateAttempt:
    """Test multiple-choice evaluation logic."""

    def test_exact_match(self):
        """GIVEN exact string match WHEN evaluating THEN correct."""
        assert evaluate_attempt("10", "10") is True

    def test_case_insensitive(self):
        """GIVEN different casing WHEN evaluating THEN correct."""
        assert evaluate_attempt("PERRO", "Perro") is True

    def test_trimmed_whitespace(self):
        """GIVEN leading/trailing whitespace WHEN evaluating THEN correct."""
        assert evaluate_attempt("  10  ", "10") is True

    def test_incorrect_answer(self):
        """GIVEN wrong answer WHEN evaluating THEN incorrect."""
        assert evaluate_attempt("9", "10") is False


class TestCalculateStaircase:
    """Test staircase progression logic."""

    def test_three_correct_level_up(self):
        """GIVEN 3 consecutive correct WHEN staircase THEN level up."""
        result = calculate_staircase(2, True, 2, 0)
        assert result["new_level"] == 3
        assert result["level_changed"] is True

    def test_two_correct_partial(self):
        """GIVEN 2 consecutive correct WHEN staircase THEN no level change."""
        result = calculate_staircase(2, True, 1, 0)
        assert result["new_level"] == 2
        assert result["level_changed"] is False
        assert result["new_consecutive_correct"] == 2

    def test_three_incorrect_level_down(self):
        """GIVEN 3 consecutive incorrect WHEN staircase THEN level down."""
        result = calculate_staircase(3, False, 0, 2)
        assert result["new_level"] == 2
        assert result["level_changed"] is True

    def test_floor_boundary(self):
        """GIVEN level 1 with incorrect streak WHEN staircase THEN stays at 1."""
        result = calculate_staircase(1, False, 0, 2)
        assert result["new_level"] == 1
        assert result["level_changed"] is False

    def test_ceiling_boundary(self):
        """GIVEN level 10 with correct streak WHEN staircase THEN stays at 10."""
        result = calculate_staircase(10, True, 2, 0)
        assert result["new_level"] == 10
        assert result["level_changed"] is False

    def test_mixed_resets_counters(self):
        """GIVEN correct after incorrect streak WHEN staircase THEN reset incorrect counter."""
        result = calculate_staircase(3, True, 0, 2)
        assert result["new_level"] == 3
        assert result["new_consecutive_correct"] == 1
        assert result["new_consecutive_incorrect"] == 0

    def test_incorrect_after_correct_resets(self):
        """GIVEN incorrect after correct streak WHEN staircase THEN reset correct counter."""
        result = calculate_staircase(3, False, 2, 0)
        assert result["new_level"] == 3
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 1
