"""Tests for IQ Practice engine."""

from core.iq_practice import calculate_staircase, evaluate_attempt


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
    """Test staircase progression logic (redistribution model).

    See ``core/staircase.py`` for the full algorithm. Key properties:
    - 5 correct (uniform) advances one level; both counters reset.
    - On incorrect with cc > 0, one unit moves from cc to ci.
    - On incorrect with cc == 0, the failure is absorbed (UX).
    - ci does NOT reset on correct — failures accumulate.
    - 3 incorrect (after redistribution) retreats one level.
    """

    def test_five_correct_level_up(self):
        """GIVEN 4 cc + 1 correct WHEN staircase THEN level up."""
        result = calculate_staircase(3, True, 4, 0)
        assert result["new_level"] == 4
        assert result["level_changed"] is True
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0

    def test_two_correct_partial(self):
        """GIVEN 1 cc + 1 correct WHEN staircase THEN no level change, cc=2."""
        result = calculate_staircase(2, True, 1, 0)
        assert result["new_level"] == 2
        assert result["level_changed"] is False
        assert result["new_consecutive_correct"] == 2

    def test_three_redistributions_level_down(self):
        """GIVEN 3 cc, 2 ci, then incorrect WHEN staircase THEN level down.

        The incorrect redistributes: cc=3-1=2, ci=2+1=3 → ci >= 3 → down.
        """
        result = calculate_staircase(3, False, 3, 2)
        assert result["new_level"] == 2
        assert result["level_changed"] is True
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0

    def test_floor_boundary(self):
        """GIVEN level 1 with cc=0 and incorrect WHEN staircase THEN stays at 1.

        UX protection: failure is absorbed (cc=0 means nothing to
        redistribute), so the level doesn't change.
        """
        result = calculate_staircase(1, False, 0, 2)
        assert result["new_level"] == 1
        assert result["level_changed"] is False
        # ci is unchanged because the failure was absorbed
        assert result["new_consecutive_incorrect"] == 2

    def test_ceiling_boundary(self):
        """GIVEN level 10 with 4 cc + 1 correct WHEN staircase THEN stays at 10.

        5 cc would level up to 11, but the cap holds at 10.
        """
        result = calculate_staircase(10, True, 4, 0)
        assert result["new_level"] == 10
        assert result["level_changed"] is False

    def test_correct_decreases_incorrect(self):
        """GIVEN ci=2 + correct WHEN staircase THEN ci decreases to 1, cc=1."""
        result = calculate_staircase(3, True, 0, 2)
        assert result["new_level"] == 3
        assert result["new_consecutive_correct"] == 1
        assert result["new_consecutive_incorrect"] == 1  # Decreased

    def test_incorrect_redistributes_from_correct(self):
        """GIVEN cc=2, ci=0 + incorrect WHEN staircase THEN cc=1, ci=1.

        In the old (consecutive) model, cc would reset to 0. In the
        new (redistribution) model, exactly one unit moves.
        """
        result = calculate_staircase(3, False, 2, 0)
        assert result["new_level"] == 3
        assert result["new_consecutive_correct"] == 1  # was 2
        assert result["new_consecutive_incorrect"] == 1  # was 0

    def test_failure_absorbed_when_no_correct_buffer(self):
        """GIVEN cc=0, ci=0 + incorrect WHEN staircase THEN no change.

        This is the core UX protection: a user starting fresh at a
        level doesn't get punished for failing the first attempt
        ("para que colocar como falla"). They can experiment without
        accumulating a frustrating failure counter.
        """
        result = calculate_staircase(3, False, 0, 0)
        assert result["new_level"] == 3
        assert result["level_changed"] is False
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0

    def test_three_failures_with_no_correct_never_level_down(self):
        """GIVEN cc=0, ci=0 + 3 incorrect WHEN staircase THEN still cc=0, ci=0.

        Confirms the UX protection end-to-end: three failures from a
        fresh state do NOT take the user down. They need to first
        accumulate correct answers before failures start counting.
        """
        state = (0, 0)  # cc, ci
        for _ in range(3):
            r = calculate_staircase(3, False, state[0], state[1])
            state = (r["new_consecutive_correct"], r["new_consecutive_incorrect"])
        assert state == (0, 0)
        # Level never changed
        # (caller would have level=3 throughout, no level_down)

    def test_four_correct_then_one_fail_partial(self):
        """GIVEN cc=4 + incorrect WHEN staircase THEN cc=3, ci=1, no level change."""
        result = calculate_staircase(3, False, 4, 0)
        assert result["new_level"] == 3
        assert result["level_changed"] is False
        assert result["new_consecutive_correct"] == 3
        assert result["new_consecutive_incorrect"] == 1
