"""
Tests for the Math Thinking Game Engine.

Covers:
- Unit tests for core.math_thinking (evaluate_attempt, calculate_staircase, generate_problem)
- Integration tests for /api/math-thinking endpoints via TestClient
"""

import math
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from core.math_thinking import (
    evaluate_attempt,
    calculate_staircase,
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
    """Level-only staircase: 3 correct -> up, 3 errors -> down, floor 1, ceiling 10."""

    def test_three_correct_levels_up(self):
        """3 correct at level 5 -> level up to 6, counters reset."""
        result = calculate_staircase(
            level=5, was_correct=True,
            consecutive_correct=2, consecutive_incorrect=0,
        )
        assert result["new_level"] == 6
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is True
        assert "nivel 6" in result["message"]

    def test_three_incorrect_levels_down(self):
        """3 incorrect at level 5 -> level down to 4, counters reset."""
        result = calculate_staircase(
            level=5, was_correct=False,
            consecutive_correct=0, consecutive_incorrect=2,
        )
        assert result["new_level"] == 4
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is True
        assert "nivel 4" in result["message"]

    def test_one_correct_from_fresh(self):
        """1 correct starting fresh -> consecutive_correct=1, no level change."""
        result = calculate_staircase(
            level=5, was_correct=True,
            consecutive_correct=0, consecutive_incorrect=0,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 1
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is False

    def test_one_incorrect_from_fresh(self):
        """1 incorrect starting fresh -> consecutive_incorrect=1, no level change."""
        result = calculate_staircase(
            level=5, was_correct=False,
            consecutive_correct=0, consecutive_incorrect=0,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 1
        assert result["level_changed"] is False

    def test_correct_streak_of_two_from_one(self):
        """2nd correct (streak was 1) -> consecutive_correct=2."""
        result = calculate_staircase(
            level=5, was_correct=True,
            consecutive_correct=1, consecutive_incorrect=0,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 2
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is False

    def test_incorrect_streak_of_two_from_one(self):
        """2nd incorrect (streak was 1) -> consecutive_incorrect=2."""
        result = calculate_staircase(
            level=5, was_correct=False,
            consecutive_correct=0, consecutive_incorrect=1,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 2
        assert result["level_changed"] is False

    def test_correct_resets_incorrect_streak(self):
        """Correct after 2 incorrect -> incorrect resets, correct=1."""
        result = calculate_staircase(
            level=5, was_correct=True,
            consecutive_correct=0, consecutive_incorrect=2,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 1
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is False

    def test_incorrect_resets_correct_streak(self):
        """Incorrect after 2 correct -> correct resets, incorrect=1."""
        result = calculate_staircase(
            level=5, was_correct=False,
            consecutive_correct=2, consecutive_incorrect=0,
        )
        assert result["new_level"] == 5
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 1
        assert result["level_changed"] is False

    def test_third_incorrect_at_level_1_floor(self):
        """3 incorrect at level 1 -> stays at 1, floor message."""
        result = calculate_staircase(
            level=1, was_correct=False,
            consecutive_correct=0, consecutive_incorrect=2,
        )
        assert result["new_level"] == 1
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is False
        assert "mínimo" in result["message"]

    def test_third_correct_at_level_10_ceiling(self):
        """3 correct at level 10 -> stays at 10, ceiling message."""
        result = calculate_staircase(
            level=10, was_correct=True,
            consecutive_correct=2, consecutive_incorrect=0,
        )
        assert result["new_level"] == 10
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 0
        assert result["level_changed"] is False
        assert "máximo" in result["message"]

    def test_message_on_correct_streak(self):
        """Partial correct shows progress counter in message."""
        result = calculate_staircase(
            level=5, was_correct=True,
            consecutive_correct=0, consecutive_incorrect=0,
        )
        assert "1/3" in result["message"]
        assert "Correcto" in result["message"]

    def test_message_on_incorrect_streak(self):
        """Partial incorrect shows error counter in message."""
        result = calculate_staircase(
            level=5, was_correct=False,
            consecutive_correct=0, consecutive_incorrect=0,
        )
        assert "1/3" in result["message"]
        assert "Incorrecto" in result["message"]


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
        patch("api.routes.math_thinking.generate_problem") as mock_gen,
        patch("api.routes.math_thinking.load_skill_config") as mock_config,
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
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == 1
        assert data["is_active"] is True
        assert data["best_level"] == 1

    def test_returns_404_for_invalid_skill_id(self, client):
        """Non-existent skill_id returns 404."""
        response = client.post(
            "/api/math-thinking/sessions", params={"skill_id": 99999}
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
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
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

    def test_returns_404_for_nonexistent_session(self, client):
        """Non-existent session ID returns 404."""
        response = client.post("/api/math-thinking/sessions/99999/rounds")
        assert response.status_code == 404

    def test_returns_400_for_inactive_session(self, client, skill_factory):
        """Consolidated (inactive) session returns 400."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
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
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
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
        assert data["solution_steps"] == []

    def test_wrong_answer_submission(self, client, skill_factory):
        """Wrong answer returns correct=False with solution steps."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
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
        """3 correct answers advance the level."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        # Submit 3 correct attempts
        for _ in range(3):
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
        assert state["level"] >= 2, "Expected level increase after 3 correct"
        assert state["consecutive_correct"] == 0  # reset after level change
        assert state["total_rounds"] == 3

    def test_updates_staircase_on_wrong(self, client, skill_factory):
        """Wrong answers increase consecutive_incorrect."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
        )
        session_id = session_resp.json()["id"]

        # Submit 2 wrong attempts
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
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
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
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
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
        from models.models import Session as PracticeSession
        from core.database import engine
        from sqlmodel import Session as DBSession

        with DBSession(engine) as db:
            ps = db.get(PracticeSession, data["practice_session_id"])
            assert ps is not None
            assert ps.skill_id == skill.id
            assert ps.duration_minutes >= 10

    def test_returns_400_if_already_consolidated(self, client, skill_factory):
        """Already consolidated session returns 400."""
        skill = skill_factory(skill_type="problem_set")
        session_resp = client.post(
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
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

    def test_returns_404_for_nonexistent_session(self, client):
        """Non-existent session returns 404."""
        response = client.post(
            "/api/math-thinking/sessions/99999/consolidate"
        )
        assert response.status_code == 404


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
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
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
            "/api/math-thinking/sessions", params={"skill_id": skill.id}
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
