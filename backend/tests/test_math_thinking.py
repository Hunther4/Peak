"""
Tests for the Math Thinking Game Engine.

Covers:
- Unit tests for core.math_thinking (evaluate_attempt, calculate_staircase, generate_problem)
- Integration tests for /api/math-thinking endpoints via TestClient
"""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from core.math_thinking import (
    calculate_staircase,
    evaluate_attempt,
    generate_problem,
)

# =============================================================================
# Helpers
# =============================================================================

def _make_mock_problem(
    question="¿Cuánto es 5 + 3?",
    correct_answer=8.0,
    solution_steps=None,
):
    """Create a mock AI response object (avoids Pydantic validation in mock)."""
    return SimpleNamespace(
        question=question,
        correct_answer=correct_answer,
        solution_steps=solution_steps or ["Sumá 5 y 3 = 8."],
    )


MINIMAL_CONFIG = {
    "difficulties": {
        1: {
            "label": "básico",
            "topics": ["suma", "resta"],
            "problem_types": ["cálculo directo"],
        },
        5: {
            "label": "avanzado",
            "topics": ["multiplicación", "división"],
            "problem_types": ["cálculo directo"],
        },
    }
}


# =============================================================================
# Unit Tests — evaluate_attempt()
# =============================================================================

class TestEvaluateAttempt:
    """Numeric comparison with tolerance of 0.01."""

    def test_exact_match(self):
        """15.0 vs 15.0 -> True."""
        assert evaluate_attempt(15.0, 15.0) is True

    def test_within_tolerance(self):
        """15.001 vs 15.0 -> True (diff < 0.01)."""
        assert evaluate_attempt(15.001, 15.0) is True

    def test_barely_outside_tolerance(self):
        """15.02 vs 15.0 -> False (diff > 0.01).

        Note: 15.01 is NOT used as a boundary test because IEEE 754
        represents 15.01 as ~15.0099999999999998, making the diff
        ~0.009999999999999787 which is *inside* the tolerance.
        """
        assert evaluate_attempt(15.02, 15.0) is False

    def test_completely_different(self):
        """15.0 vs 20.0 -> False."""
        assert evaluate_attempt(15.0, 20.0) is False

    def test_negative_numbers_match(self):
        """-5.0 vs -5.0 -> True."""
        assert evaluate_attempt(-5.0, -5.0) is True

    def test_negative_within_tolerance(self):
        """-5.001 vs -5.0 -> True (diff < 0.01)."""
        assert evaluate_attempt(-5.001, -5.0) is True

    def test_zero_within_tolerance(self):
        """0.0 vs 0.001 -> True."""
        assert evaluate_attempt(0.0, 0.001) is True

    def test_zero_vs_large(self):
        """0.0 vs 42.0 -> False (completely wrong)."""
        assert evaluate_attempt(0.0, 42.0) is False

    def test_just_inside_boundary(self):
        """15.009999 vs 15.0 -> True (diff < 0.01)."""
        assert evaluate_attempt(15.009999, 15.0) is True

    def test_integer_arguments(self):
        """Integer inputs work correctly."""
        assert evaluate_attempt(5, 5) is True
        assert evaluate_attempt(5, 6) is False


# =============================================================================
# Unit Tests — calculate_staircase()
# =============================================================================

class TestCalculateStaircase:
    """Redistribution staircase: 5 correct -> up, 3 errors -> down.

    See ``core/staircase.py`` for the full algorithm. Key properties:
    - 5 correct (uniform) advances one level; both counters reset.
    - On incorrect with cc > 0, one unit moves from cc to ci.
    - On incorrect with cc == 0, the failure is absorbed (UX).
    - ci does NOT reset on correct — failures accumulate.
    - 3 incorrect (after redistribution) retreats one level.
    """

    def test_five_correct_levels_up(self):
        """5th correct (4 cc + 1) at level 5 -> level up to 6, counters reset."""
        result = calculate_staircase(
            level=5, was_correct=True,
            consecutive_correct=4, consecutive_incorrect=0,
        )
        assert result["new_level"] == 6
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is True
        assert "nivel 6" in result["message"]

    def test_three_redistributions_levels_down(self):
        """3rd redistribution (cc=3,ci=2 + incorrect) at level 5 -> level down to 4."""
        result = calculate_staircase(
            level=5, was_correct=False,
            consecutive_correct=3, consecutive_incorrect=2,
        )
        assert result["new_level"] == 4
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is True
        assert "nivel 4" in result["message"]

    def test_one_correct_from_fresh(self):
        """1 correct starting fresh -> cc=1, no level change."""
        result = calculate_staircase(
            level=5, was_correct=True,
            consecutive_correct=0, consecutive_incorrect=0,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 1
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is False

    def test_one_incorrect_from_fresh_absorbed(self):
        """1 incorrect starting fresh (cc=0) -> failure absorbed, no change.

        UX protection: no correct buffer to redistribute, so the
        failure is silently dropped. This avoids the "1/3 errores"
        message on the very first attempt.
        """
        result = calculate_staircase(
            level=5, was_correct=False,
            consecutive_correct=0, consecutive_incorrect=0,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0  # NOT incremented
        assert result["level_changed"] is False

    def test_two_corrects_from_one(self):
        """2nd correct (cc=1) -> cc=2, no level change."""
        result = calculate_staircase(
            level=5, was_correct=True,
            consecutive_correct=1, consecutive_incorrect=0,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 2
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is False

    def test_incorrect_redistributes_from_correct(self):
        """Incorrect after cc=2 -> cc=1, ci=1, no level change.

        Old (consecutive) model would set cc=0. New (redistribution)
        model moves exactly one unit.
        """
        result = calculate_staircase(
            level=5, was_correct=False,
            consecutive_correct=2, consecutive_incorrect=0,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 1
        assert result["new_consecutive_incorrect"] == 1
        assert result["level_changed"] is False

    def test_correct_decreases_incorrect(self):
        """Correct with ci=2 -> cc=1, ci decreases to 1."""
        result = calculate_staircase(
            level=5, was_correct=True,
            consecutive_correct=0, consecutive_incorrect=2,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 1
        assert result["new_consecutive_incorrect"] == 1  # Decreased
        assert result["level_changed"] is False

    def test_floor_at_level_1_with_cc_zero(self):
        """Level 1 with cc=0 + incorrect -> failure absorbed, no change.

        UX protection at the floor: failure absorbed because cc=0.
        The "mínimo" floor message only triggers when a redistribution
        would push the level below 1 (e.g., cc=3, ci=2 + incorrect
        would make ci=3 and try to go to level 0, capped at 1).
        """
        result = calculate_staircase(
            level=1, was_correct=False,
            consecutive_correct=0, consecutive_incorrect=2,
        )
        assert result["new_level"] == 1
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 2  # absorbed, not reset
        assert result["level_changed"] is False
        # No "mínimo" because the failure was absorbed, not redistributed

    def test_floor_message_when_redistribution_would_underflow(self):
        """Level 1 with cc=3, ci=2 + incorrect -> ci=3 triggers floor message.

        The redistribution (cc-1, ci+1) brings ci to 3, which would
        drop the level to 0, but the floor keeps it at 1.
        """
        result = calculate_staircase(
            level=1, was_correct=False,
            consecutive_correct=3, consecutive_incorrect=2,
        )
        assert result["new_level"] == 1
        assert result["level_changed"] is False
        assert "mínimo" in result["message"]

    def test_ceiling_at_level_10(self):
        """5th correct at level 10 -> stays at 10, ceiling message."""
        result = calculate_staircase(
            level=10, was_correct=True,
            consecutive_correct=4, consecutive_incorrect=0,
        )
        assert result["new_level"] == 10
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is False
        assert "máximo" in result["message"]

    def test_message_on_partial_correct(self):
        """Partial correct shows '1/5 para subir' in message."""
        result = calculate_staircase(
            level=5, was_correct=True,
            consecutive_correct=0, consecutive_incorrect=0,
        )
        assert "1/5" in result["message"]
        assert "Correcto" in result["message"]

    def test_message_on_redistribution(self):
        """Redistribution shows progress in both counters in message."""
        result = calculate_staircase(
            level=5, was_correct=False,
            consecutive_correct=2, consecutive_incorrect=0,
        )
        assert "1/3" in result["message"]
        assert "Incorrecto" in result["message"]

    def test_message_on_absorbed_failure(self):
        """Absorbed failure (cc=0) shows friendly message, no counter."""
        result = calculate_staircase(
            level=5, was_correct=False,
            consecutive_correct=0, consecutive_incorrect=0,
        )
        assert "Incorrecto" in result["message"]
        assert "1/3" not in result["message"]  # no counter shown
        assert "Seguí" in result["message"] or "intentando" in result["message"]

    def test_three_failures_with_no_correct_never_level_down(self):
        """GIVEN cc=0 + 3 incorrect WHEN staircase THEN never level down.

        End-to-end: three failures from a fresh state do NOT take the
        user down. They need to first accumulate correct answers
        before failures start counting.
        """
        state = (0, 0)
        for _ in range(3):
            r = calculate_staircase(
                level=5, was_correct=False,
                consecutive_correct=state[0], consecutive_incorrect=state[1],
            )
            state = (r["new_consecutive_correct"], r["new_consecutive_incorrect"])
        assert state == (0, 0)  # nothing was redistributed


# =============================================================================
# Unit Tests — generate_problem()
# =============================================================================

class TestGenerateProblem:
    """AI problem generation: prompt building, retry logic, fallback."""

    def test_valid_response(self):
        """Valid AI response returns question, answer, and steps."""
        def mock_router(task_type, system_prompt, user_prompt, response_model):
            return _make_mock_problem(
                question="¿Cuánto es 5 + 3?",
                correct_answer=8.0,
                solution_steps=["Sumá 5 y 3 = 8."],
            )

        result = generate_problem(5, MINIMAL_CONFIG, mock_router)
        assert result["question"] == "¿Cuánto es 5 + 3?"
        assert result["correct_answer"] == 8.0
        assert result["solution_steps"] == ["Sumá 5 y 3 = 8."]

    def test_prompt_construction(self):
        """Prompts include correct level, label, and topics."""
        captured = {}

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            captured["system"] = system_prompt
            captured["user"] = user_prompt
            return _make_mock_problem()

        generate_problem(5, MINIMAL_CONFIG, mock_router)

        assert "nivel 5" in captured["system"]
        assert "avanzado" in captured["system"]
        assert "multiplicación" in captured["user"]
        assert "división" in captured["user"]

    def test_prompt_fallback_to_default_on_missing_level(self):
        """Missing level config falls back to level 1 defaults."""
        captured = {}

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            captured["system"] = system_prompt
            captured["user"] = user_prompt
            return _make_mock_problem()

        generate_problem(5, {"difficulties": {}}, mock_router)

        assert "básico" in captured["system"]
        assert "suma" in captured["user"]

    def test_none_response_triggers_retry(self):
        """Router returns None first, then valid on retry."""
        responses = iter([
            None,
            _make_mock_problem(
                question="Retry question",
                correct_answer=99.0,
                solution_steps=["Step 1"],
            ),
        ])

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            return next(responses)

        result = generate_problem(5, MINIMAL_CONFIG, mock_router)
        assert result["question"] == "Retry question"
        assert result["correct_answer"] == 99.0

    def test_none_answer_triggers_retry(self):
        """Answer is None -> retry with stricter prompt."""
        responses = iter([
            _make_mock_problem(correct_answer=None),
            _make_mock_problem(correct_answer=42.0),
        ])

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            return next(responses)

        result = generate_problem(5, MINIMAL_CONFIG, mock_router)
        assert result["correct_answer"] == 42.0

    def test_nan_answer_triggers_retry(self):
        """Answer is NaN -> retry with stricter prompt."""
        responses = iter([
            _make_mock_problem(correct_answer=float("nan")),
            _make_mock_problem(correct_answer=42.0),
        ])

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            return next(responses)

        result = generate_problem(5, MINIMAL_CONFIG, mock_router)
        assert result["correct_answer"] == 42.0

    def test_inf_answer_triggers_retry(self):
        """Answer is inf -> retry with stricter prompt."""
        responses = iter([
            _make_mock_problem(correct_answer=float("inf")),
            _make_mock_problem(correct_answer=42.0),
        ])

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            return next(responses)

        result = generate_problem(5, MINIMAL_CONFIG, mock_router)
        assert result["correct_answer"] == 42.0

    def test_string_answer_triggers_retry(self):
        """Answer is a non-numeric string -> retry."""
        responses = iter([
            _make_mock_problem(correct_answer="not a number"),
            _make_mock_problem(correct_answer=42.0),
        ])

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            return next(responses)

        result = generate_problem(5, MINIMAL_CONFIG, mock_router)
        assert result["correct_answer"] == 42.0

    def test_all_three_attempts_fail_fallback(self):
        """All 3 attempts fail -> fallback to '2 + 2' = 4."""
        call_count = 0

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            nonlocal call_count
            call_count += 1
            return None

        result = generate_problem(5, MINIMAL_CONFIG, mock_router)
        assert call_count == 3
        assert result["question"] == "¿Cuánto es 2 + 2?"
        assert result["correct_answer"] == 4.0
        assert result["solution_steps"] == ["Sumá 2 + 2 = 4."]

    def test_retry_prompt_includes_error_context(self):
        """Retry prompt mentions the previous error."""
        prompts = []
        responses = iter([
            None,
            _make_mock_problem(),
        ])

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            prompts.append(user_prompt)
            return next(responses)

        generate_problem(5, MINIMAL_CONFIG, mock_router)
        assert len(prompts) == 2
        assert "DEBE" in prompts[1]  # Stricter instruction on retry
        assert "no devolvió" in prompts[1]  # Previous error is mentioned

    def test_mixed_invalid_then_valid_at_last_attempt(self):
        """Succeeds on the 3rd and final retry."""
        responses = iter([
            None,
            None,
            _make_mock_problem(correct_answer=7.0),
        ])

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            return next(responses)

        result = generate_problem(5, MINIMAL_CONFIG, mock_router)
        assert result["correct_answer"] == 7.0

    def test_all_invalid_types_exhaust_retries(self):
        """Different invalid types across all 3 attempts -> fallback."""
        responses = iter([
            None,
            _make_mock_problem(correct_answer=float("nan")),
            _make_mock_problem(correct_answer=float("inf")),
        ])

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            return next(responses)

        result = generate_problem(5, MINIMAL_CONFIG, mock_router)
        assert result["question"] == "¿Cuánto es 2 + 2?"
        assert result["correct_answer"] == 4.0


# =============================================================================
# Integration Tests — AI mock fixture (autouse for all tests in this module)
# =============================================================================
# Patches at the route level to intercept imported references without
# affecting unit tests which import directly from core.math_thinking.


@pytest.fixture(autouse=True)
def mock_math_thinking_ai():
    """Mock AI-dependent route functions to avoid real AI calls and file I/O.

    Patches ``api.routes.math_thinking.generate_problem`` (the route's local
    reference to the engine function) so POST /sessions/{id}/rounds returns a
    fixed problem instead of calling the AI router.

    Also patches ``load_skill_config`` so it doesn't try to open the YAML
    config file (relative path issues in test runner CWD).

    Does NOT affect unit tests: they import ``generate_problem`` directly from
    ``core.math_thinking``, not from the route module.
    """
    with (
        patch("services.math_thinking_service.generate_problem") as mock_gen,
        patch("services.math_thinking_service.load_skill_config") as mock_config,
    ):
        mock_gen.return_value = {
            "question": "¿Cuánto es 5 + 3?",
            "correct_answer": 8.0,
            "solution_steps": ["Sumá 5 y 3 = 8."],
        }
        mock_config.return_value = {"difficulties": {}}
        yield


# =============================================================================
# Integration Tests — POST /api/math-thinking/sessions
# =============================================================================


class TestCreateSession:
    """POST /api/math-thinking/sessions"""

    def test_creates_session_with_correct_structure(self, client, skill_factory):
        """Creates a math thinking session with default values."""
        skill = skill_factory(skill_type="problem_set")
        response = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == 1
        assert data["is_active"] is True
        assert data["best_level"] == 1

    def test_returns_404_for_invalid_skill_id(self, client):
        """Non-existent skill_id returns 404."""
        response = client.post(
            "/api/math-thinking/sessions", json={"skill_id": 99999}
        )
        assert response.status_code == 404


# =============================================================================
# Integration Tests — POST /api/math-thinking/sessions/{id}/rounds
# =============================================================================


class TestCreateRound:
    """POST /api/math-thinking/sessions/{id}/rounds"""

    def test_creates_round_with_problem_and_level(self, client, skill_factory):
        """Creates a round with AI-generated problem at session level."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        response = client.post(
            f"/api/math-thinking/sessions/{session_id}/rounds"
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["level"] == 1
        assert data["problem_text"] == "¿Cuánto es 5 + 3?"

    def test_returns_400_for_nonexistent_session(self, client):
        """Non-existent session ID returns 400 (ValueError)."""
        response = client.post("/api/math-thinking/sessions/99999/rounds")
        assert response.status_code == 400

    def test_returns_400_for_inactive_session(self, client, skill_factory):
        """Consolidated (inactive) session returns 400."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        # Create 3 rounds
        for _ in range(3):
            client.post(f"/api/math-thinking/sessions/{session_id}/rounds")

        # Consolidate to make inactive
        client.post(f"/api/math-thinking/sessions/{session_id}/consolidate")

        # Now try to add a round
        response = client.post(
            f"/api/math-thinking/sessions/{session_id}/rounds"
        )
        assert response.status_code == 400
        assert "closed" in response.json()["detail"].lower()


# =============================================================================
# Integration Tests — POST /api/math-thinking/rounds/{id}/attempts
# =============================================================================


class TestSubmitAttempt:
    """POST /api/math-thinking/rounds/{id}/attempts"""

    def test_correct_answer_submission(self, client, skill_factory):
        """Correct answer returns correct=True."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]
        round_resp = client.post(
            f"/api/math-thinking/sessions/{session_id}/rounds"
        )
        round_id = round_resp.json()["id"]

        response = client.post(
            f"/api/math-thinking/rounds/{round_id}/attempts",
            json={"user_answer": 8.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["correct"] is True
        assert len(data["solution_steps"]) > 0  # Steps always returned now

    def test_wrong_answer_submission(self, client, skill_factory):
        """Wrong answer returns correct=False with solution steps."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]
        round_resp = client.post(
            f"/api/math-thinking/sessions/{session_id}/rounds"
        )
        round_id = round_resp.json()["id"]

        response = client.post(
            f"/api/math-thinking/rounds/{round_id}/attempts",
            json={"user_answer": 999.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["correct"] is False
        assert len(data["solution_steps"]) > 0

    def test_updates_staircase_on_correct(self, client, skill_factory):
        """5 correct answers at level 1 advance to level 2 (adaptive staircase).

        The new pool rotates through 8 daily-life problems with different
        answers, so we mock the pool to return a known problem with
        correct_answer=8.0 to make the test deterministic.
        """
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        mock_problem = {
            "question": "¿Cuánto es 5 + 3?",
            "correct_answer": 8.0,
            "solution_steps": ["Sumá 5 y 3 = 8."],
            "source": "Test mock",
        }

        with patch("core.math_thinking.get_pool_puzzle", return_value=mock_problem):
            # Submit 5 correct attempts (adaptive staircase: 5 for levels 1-2)
            for _ in range(5):
                round_resp = client.post(
                    f"/api/math-thinking/sessions/{session_id}/rounds"
                )
                round_id = round_resp.json()["id"]
                client.post(
                    f"/api/math-thinking/rounds/{round_id}/attempts",
                    json={"user_answer": 8.0},
                )

        # Check session state — level should have increased
        state_resp = client.get(
            f"/api/math-thinking/sessions/{session_id}/state"
        )
        state = state_resp.json()
        assert state["level"] >= 2, "Expected level increase after 5 correct"
        assert state["consecutive_correct"] == 0  # reset after level change
        assert state["total_rounds"] == 5

    def test_updates_staircase_on_wrong(self, client, skill_factory):
        """Wrong answers from fresh state are absorbed (UX protection).

        With the redistribution model, a failure only counts when
        there are correct answers to redistribute from. From a fresh
        state (consecutive_correct=0), the failure is silently dropped
        ("para que colocar como falla") so the user can experiment
        without accumulating a frustrating failure counter.
        """
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        # Submit 2 wrong attempts from fresh state (cc=0)
        for _ in range(2):
            round_resp = client.post(
                f"/api/math-thinking/sessions/{session_id}/rounds"
            )
            round_id = round_resp.json()["id"]
            client.post(
                f"/api/math-thinking/rounds/{round_id}/attempts",
                json={"user_answer": 999.0},
            )

        state_resp = client.get(
            f"/api/math-thinking/sessions/{session_id}/state"
        )
        state = state_resp.json()
        # Both failures absorbed — ci stays at 0
        assert state["consecutive_incorrect"] == 0
        assert state["consecutive_correct"] == 0

    def test_wrong_after_correct_redistributes(self, client, skill_factory):
        """Wrong after correct counts via redistribution (cc-1, ci+1)."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        mock_problem = {
            "question": "¿Cuánto es 5 + 3?",
            "correct_answer": 8.0,
            "solution_steps": ["Sumá 5 y 3 = 8."],
            "source": "Test mock",
        }

        with patch("core.math_thinking.get_pool_puzzle", return_value=mock_problem):
            # First: 2 correct (build up cc=2)
            for _ in range(2):
                round_resp = client.post(
                    f"/api/math-thinking/sessions/{session_id}/rounds"
                )
                round_id = round_resp.json()["id"]
                client.post(
                    f"/api/math-thinking/rounds/{round_id}/attempts",
                    json={"user_answer": 8.0},
                )
            # Then: 2 wrong — first redistributes (cc=1, ci=1),
            #       second redistributes (cc=0, ci=2)
            for _ in range(2):
                round_resp = client.post(
                    f"/api/math-thinking/sessions/{session_id}/rounds"
                )
                round_id = round_resp.json()["id"]
                client.post(
                    f"/api/math-thinking/rounds/{round_id}/attempts",
                    json={"user_answer": 999.0},
                )

        state_resp = client.get(
            f"/api/math-thinking/sessions/{session_id}/state"
        )
        state = state_resp.json()
        assert state["consecutive_incorrect"] == 2
        assert state["consecutive_correct"] == 0

    def test_returns_404_for_nonexistent_round(self, client):
        """Non-existent round returns 404."""
        response = client.post(
            "/api/math-thinking/rounds/99999/attempts",
            json={"user_answer": 8.0},
        )
        assert response.status_code == 404


# =============================================================================
# Integration Tests — POST /api/math-thinking/sessions/{id}/consolidate
# =============================================================================


class TestConsolidateSession:
    """POST /api/math-thinking/sessions/{id}/consolidate"""

    def test_returns_400_if_less_than_3_rounds(self, client, skill_factory):
        """Consolidation requires at least 3 rounds."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        # Only 1 round
        client.post(f"/api/math-thinking/sessions/{session_id}/rounds")

        response = client.post(
            f"/api/math-thinking/sessions/{session_id}/consolidate"
        )
        assert response.status_code == 400
        assert "Minimum 3" in response.json()["detail"]

    def test_consolidates_and_creates_practice_session(
        self, client, skill_factory
    ):
        """Successful consolidation creates a PracticeSession."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        # Create 3 rounds
        for _ in range(3):
            client.post(f"/api/math-thinking/sessions/{session_id}/rounds")

        response = client.post(
            f"/api/math-thinking/sessions/{session_id}/consolidate"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "consolidated"
        assert "practice_session_id" in data
        assert data["rounds_completed"] == 3

        # Verify the PracticeSession exists
        from sqlmodel import Session as DBSession

        from core.database import engine
        from models.models import Session as PracticeSession

        with DBSession(engine) as db:
            ps = db.get(PracticeSession, data["practice_session_id"])
            assert ps is not None
            assert ps.skill_id == skill.id
            assert ps.duration_minutes >= 10

    def test_returns_400_if_already_consolidated(self, client, skill_factory):
        """Already consolidated session returns 400."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        # Create 3 rounds and consolidate
        for _ in range(3):
            client.post(f"/api/math-thinking/sessions/{session_id}/rounds")
        client.post(f"/api/math-thinking/sessions/{session_id}/consolidate")

        # Try again
        response = client.post(
            f"/api/math-thinking/sessions/{session_id}/consolidate"
        )
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_returns_400_for_nonexistent_session(self, client):
        """Non-existent session returns 400 (ValueError)."""
        response = client.post(
            "/api/math-thinking/sessions/99999/consolidate"
        )
        assert response.status_code == 400


# =============================================================================
# Integration Tests — GET /api/math-thinking/sessions/{id}/state
# =============================================================================


class TestGetState:
    """GET /api/math-thinking/sessions/{id}/state"""

    def test_returns_session_state_with_correct_structure(
        self, client, skill_factory
    ):
        """Returns current session state with expected fields."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        response = client.get(
            f"/api/math-thinking/sessions/{session_id}/state"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == 1
        assert data["consecutive_correct"] == 0
        assert data["consecutive_incorrect"] == 0
        assert data["total_rounds"] == 0
        assert data["is_active"] is True
        assert data["best_level"] == 1

    def test_returns_404_for_nonexistent_session(self, client):
        """Non-existent session returns 404."""
        response = client.get("/api/math-thinking/sessions/99999/state")
        assert response.status_code == 404


# =============================================================================
# Integration Tests — GET /api/math-thinking/sessions/{id}/history
# =============================================================================


class TestGetHistory:
    """GET /api/math-thinking/sessions/{id}/history"""

    def test_returns_rounds_with_attempt_data(self, client, skill_factory):
        """Returns rounds with attempt data."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", json={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        # Create a round and submit an attempt
        round_resp = client.post(
            f"/api/math-thinking/sessions/{session_id}/rounds"
        )
        round_data = round_resp.json()
        client.post(
            f"/api/math-thinking/rounds/{round_data['id']}/attempts",
            json={"user_answer": 8.0},
        )

        response = client.get(
            f"/api/math-thinking/sessions/{session_id}/history"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["rounds"]) == 1
        assert data["rounds"][0]["id"] == round_data["id"]
        assert data["rounds"][0]["correct"] is True
        assert len(data["rounds"][0]["attempts"]) == 1
        assert data["rounds"][0]["attempts"][0]["correct"] is True
        assert data["rounds"][0]["attempts"][0]["user_answer"] == 8.0
