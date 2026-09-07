"""
Direct service-layer tests for math_thinking_service.

Bypasses the FastAPI HTTP layer to validate the service functions in
isolation. Catches logic bugs without going through routing, validation,
or middleware (auth, rate limit, etc.).

Each test exercises a single public function:
- iniciar_sesion
- crear_round
- enviar_intento
- consolidar_sesion
"""
import json
from unittest.mock import patch

import pytest

from models.models import (
    MathThinkingRound,
    MathThinkingSession,
)
from models.models import Session as PracticeSession
from services import math_thinking_service

# =============================================================================
# AI mock (autouse) — service depends on generate_problem + load_skill_config
# =============================================================================


@pytest.fixture(autouse=True)
def mock_math_thinking_ai():
    """Mock AI-dependent service functions so tests run offline.

    Patches at the service module (services.math_thinking_service.*) so
    the service's local references are replaced. Does NOT affect
    unit tests of core.math_thinking, which import directly from core.
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
# Helpers — build state directly to control staircase inputs precisely
# =============================================================================


def _create_mt_session(db, skill_id):
    """Create a fresh MathThinkingSession and return it."""
    mt = MathThinkingSession(skill_id=skill_id)
    db.add(mt)
    db.commit()
    db.refresh(mt)
    return mt


def _create_mt_round(db, mt_session, correct_answer=8.0):
    """Create a round with a known correct_answer for deterministic tests."""
    rnd = MathThinkingRound(
        session_id=mt_session.id,
        level=mt_session.level,
        problem_text="¿Cuánto es 5 + 3?",
        correct_answer=correct_answer,
        solution_steps_json=json.dumps(["Sumá 5 y 3 = 8."]),
    )
    db.add(rnd)
    db.commit()
    db.refresh(rnd)
    return rnd


# =============================================================================
# iniciar_sesion
# =============================================================================


class TestIniciarSesion:
    """math_thinking_service.iniciar_sesion(db, skill_id)"""

    def test_iniciar_sesion_creates_session(self, session, skill_factory):
        """Verify session created with correct defaults."""
        skill = skill_factory(skill_type="problem_set")

        mt = math_thinking_service.iniciar_sesion(session, skill.id)

        assert mt.id is not None
        assert mt.skill_id == skill.id
        assert mt.level == 1
        assert mt.best_level == 1
        assert mt.is_active is True
        assert mt.consecutive_correct == 0
        assert mt.consecutive_incorrect == 0
        assert mt.total_rounds == 0
        assert mt.consolidated_session_id is None

    def test_iniciar_sesion_invalid_skill(self, session):
        """Raises ValueError for bad skill_id."""
        with pytest.raises(ValueError, match="Skill not found"):
            math_thinking_service.iniciar_sesion(session, 99999)


# =============================================================================
# crear_round
# =============================================================================


class TestCrearRound:
    """math_thinking_service.crear_round(db, session_id) -> (round, problem)"""

    def test_crear_round_generates_problem(self, session, skill_factory):
        """Verify round created with AI-generated problem and session total incremented."""
        skill = skill_factory(skill_type="problem_set")
        mt = math_thinking_service.iniciar_sesion(session, skill.id)

        round_obj, problem = math_thinking_service.crear_round(session, mt.id)

        assert round_obj.id is not None
        assert round_obj.session_id == mt.id
        assert round_obj.level == 1
        assert round_obj.problem_text == "¿Cuánto es 5 + 3?"
        assert round_obj.correct_answer == 8.0
        assert json.loads(round_obj.solution_steps_json) == ["Sumá 5 y 3 = 8."]
        assert problem["question"] == "¿Cuánto es 5 + 3?"
        assert problem["correct_answer"] == 8.0
        # Session counter advanced
        session.refresh(mt)
        assert mt.total_rounds == 1

    def test_crear_round_invalid_session(self, session):
        """Raises ValueError for bad session_id."""
        with pytest.raises(ValueError, match="Math session not found"):
            math_thinking_service.crear_round(session, 99999)


# =============================================================================
# enviar_intento
# =============================================================================


class TestEnviarIntento:
    """math_thinking_service.enviar_intento(db, round_id, user_answer)"""

    def test_enviar_intento_correct_answer(self, session, skill_factory):
        """Correct answer: correct=True, cc increments (1 correct from fresh)."""
        skill = skill_factory(skill_type="problem_set")
        mt = _create_mt_session(session, skill.id)
        rnd = _create_mt_round(session, mt, correct_answer=8.0)

        result = math_thinking_service.enviar_intento(session, rnd.id, 8.0)

        assert result["correct"] is True
        # Solution steps always returned now (collapsed in UI by default)
        assert len(result["solution_steps"]) > 0
        session.refresh(mt)
        assert mt.consecutive_correct == 1
        assert mt.consecutive_incorrect == 0
        # Attempt row created
        attempts = session.exec(
            __import__("sqlmodel").select(
                __import__("models.models", fromlist=["MathThinkingAttempt"]).MathThinkingAttempt
            ).where(
                __import__("models.models", fromlist=["MathThinkingAttempt"]).MathThinkingAttempt.round_id == rnd.id
            )
        ).all()
        assert len(attempts) == 1
        assert attempts[0].correct is True
        assert attempts[0].user_answer == 8.0

    def test_enviar_intento_incorrect_answer(self, session, skill_factory):
        """Incorrect answer: correct=False, ci increments via redistribution.

        The staircase uses a redistribution model: a wrong answer with
        cc > 0 moves one unit from cc to ci. Starting from cc=0, the
        failure is absorbed (UX protection). We pre-set cc=1 so the
        failure is redistributed and ci increments.
        """
        skill = skill_factory(skill_type="problem_set")
        mt = _create_mt_session(session, skill.id)
        mt.consecutive_correct = 1
        session.add(mt)
        session.commit()
        rnd = _create_mt_round(session, mt, correct_answer=8.0)

        result = math_thinking_service.enviar_intento(session, rnd.id, 999.0)

        assert result["correct"] is False
        # Solution steps revealed on error
        assert len(result["solution_steps"]) > 0
        session.refresh(mt)
        # ci incremented, cc decremented
        assert mt.consecutive_incorrect == 1
        assert mt.consecutive_correct == 0


# =============================================================================
# consolidar_sesion
# =============================================================================


class TestCrearRoundExtended:
    """Additional edge cases for crear_round."""

    def test_crear_round_closed_session(self, session, skill_factory):
        """Raises ValueError if session is already closed (is_active=False)."""
        skill = skill_factory(skill_type="problem_set")
        mt = _create_mt_session(session, skill.id)
        mt.is_active = False
        session.add(mt)
        session.commit()

        with pytest.raises(ValueError, match="already closed"):
            math_thinking_service.crear_round(session, mt.id)


class TestEnviarIntentoExtended:
    """Additional edge cases for enviar_intento."""

    def test_enviar_intento_invalid_round(self, session):
        """Raises ValueError for bad round_id."""
        with pytest.raises(ValueError, match="Round not found"):
            math_thinking_service.enviar_intento(session, 99999, 5.0)

    def test_enviar_intento_staircase_level_up(self, session, skill_factory):
        """Multiple correct answers trigger level up via staircase."""
        skill = skill_factory(skill_type="problem_set")
        mt = _create_mt_session(session, skill.id)

        # Simulate 4 correct answers to reach cc=4 (threshold is 5).
        # We check the staircase result propagates.
        from unittest.mock import patch

        with patch("services.math_thinking_service.calculate_staircase") as mock_stair:
            mock_stair.return_value = {
                "new_level": 2,
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
                "level_changed": True,
                "message": "¡Pasaste al nivel 2!",
            }
            rnd = _create_mt_round(session, mt, correct_answer=8.0)
            result = math_thinking_service.enviar_intento(session, rnd.id, 8.0)

            assert result["correct"] is True
            assert result["staircase_result"]["level_changed"] is True
            assert result["staircase_result"]["new_level"] == 2

            session.refresh(mt)
            assert mt.level == 2
            assert mt.best_level == 2

    def test_enviar_intento_staircase_level_down(self, session, skill_factory):
        """Multiple incorrect answers trigger level down via staircase."""
        skill = skill_factory(skill_type="problem_set")
        mt = _create_mt_session(session, skill.id)
        mt.level = 3
        session.add(mt)
        session.commit()

        from unittest.mock import patch

        with patch("services.math_thinking_service.calculate_staircase") as mock_stair:
            mock_stair.return_value = {
                "new_level": 2,
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
                "level_changed": True,
                "message": "Bajaste al nivel 2. Seguí practicando.",
            }
            rnd = _create_mt_round(session, mt, correct_answer=8.0)
            result = math_thinking_service.enviar_intento(session, rnd.id, 999.0)

            assert result["correct"] is False
            session.refresh(mt)
            assert mt.level == 2


class TestConsolidarSesion:
    """math_thinking_service.consolidar_sesion(db, session_id, elapsed_seconds)"""

    def test_consolidar_sesion_minimum_rounds(self, session, skill_factory):
        """Raises ValueError if < 3 rounds."""
        skill = skill_factory(skill_type="problem_set")
        mt = _create_mt_session(session, skill.id)
        # total_rounds starts at 0; force it below 3 to be explicit
        mt.total_rounds = 2
        session.add(mt)
        session.commit()

        with pytest.raises(ValueError, match="Minimum 3 problems required"):
            math_thinking_service.consolidar_sesion(
                session, mt.id, elapsed_seconds=60
            )
        # Session must remain active after the failed attempt
        session.refresh(mt)
        assert mt.is_active is True
        assert mt.consolidated_session_id is None

    def test_consolidar_sesion_creates_practice_session(self, session, skill_factory):
        """Verify atomic link: PracticeSession created, mt_session deactivated and linked."""
        skill = skill_factory(skill_type="problem_set")
        mt = _create_mt_session(session, skill.id)
        mt.total_rounds = 3
        mt.best_level = 2
        session.add(mt)
        session.commit()

        result = math_thinking_service.consolidar_sesion(
            session, mt.id, elapsed_seconds=120
        )

        assert result["status"] == "consolidated"
        assert result["practice_session_id"] is not None
        assert result["rounds_completed"] == 3
        assert result["best_level"] == 2

        # PracticeSession exists with correct skill
        ps = session.get(PracticeSession, result["practice_session_id"])
        assert ps is not None
        assert ps.skill_id == skill.id
        assert ps.entry_mode == "quick"
        assert ps.duration_minutes >= 10

        # Atomic link: mt_session is deactivated and references ps.id
        session.refresh(mt)
        assert mt.is_active is False
        assert mt.consolidated_session_id == ps.id
        assert mt.consolidated_session_id == result["practice_session_id"]

    def test_consolidar_sesion_already_consolidated(self, session, skill_factory):
        """Raises ValueError if session already consolidated."""
        skill = skill_factory(skill_type="problem_set")
        mt = _create_mt_session(session, skill.id)
        mt.total_rounds = 5
        mt.is_active = False  # already deactivated
        session.add(mt)
        session.commit()

        with pytest.raises(ValueError, match="already consolidated"):
            math_thinking_service.consolidar_sesion(session, mt.id, elapsed_seconds=60)

    def test_consolidar_sesion_custom_min_rounds_message(self, session, skill_factory):
        """Uses min_rounds_message for the error text."""
        skill = skill_factory(skill_type="problem_set")
        mt = _create_mt_session(session, skill.id)
        mt.total_rounds = 1
        session.add(mt)
        session.commit()

        with pytest.raises(ValueError, match="Minimum 3 problems required before consolidation"):
            math_thinking_service.consolidar_sesion(session, mt.id, elapsed_seconds=60)

    def test_consolidar_sesion_no_elapsed_seconds(self, session, skill_factory):
        """Consolidation works without elapsed_seconds."""
        skill = skill_factory(skill_type="problem_set")
        mt = _create_mt_session(session, skill.id)
        mt.total_rounds = 3
        mt.best_level = 2
        session.add(mt)
        session.commit()

        result = math_thinking_service.consolidar_sesion(session, mt.id, elapsed_seconds=None)

        assert result["status"] == "consolidated"
        ps = session.get(PracticeSession, result["practice_session_id"])
        session_data = json.loads(ps.session_data)
        assert "elapsed_seconds" not in session_data
