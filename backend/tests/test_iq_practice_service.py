"""
Direct service-layer tests for iq_practice_service.

Bypasses the FastAPI HTTP layer to validate the service functions in
isolation.
"""
import json
from unittest.mock import patch

import pytest

from models.models import IQPracticeRound, IQPracticeSession
from models.models import Session as PracticeSession
from services import iq_practice_service

# =============================================================================
# AI mock (autouse) — service depends on generate_puzzle, load_skill_config
# =============================================================================


@pytest.fixture(autouse=True)
def mock_iq_practice_ai():
    """Mock AI-dependent service functions so tests run offline."""
    with (
        patch("services.iq_practice_service.generate_puzzle") as mock_gen,
        patch("services.iq_practice_service.load_skill_config") as mock_config,
        patch("services.iq_practice_service.evaluate_attempt") as mock_eval,
        patch("services.iq_practice_service.calculate_staircase") as mock_stair,
        patch("services.iq_practice_service.record_error"),
    ):
        mock_gen.return_value = {
            "question": "¿Qué número sigue? 2, 4, 6, 8, ?",
            "options": ["9", "10", "11", "12"],
            "correct_answer": "10",
            "explanation": "La secuencia suma 2 cada vez.",
            "puzzle_type": "number_sequence",
            "source": None,
        }
        mock_config.return_value = {"levels": {}}
        mock_eval.return_value = True
        mock_stair.return_value = {
            "new_level": 1,
            "new_consecutive_correct": 1,
            "new_consecutive_incorrect": 0,
            "level_changed": False,
            "message": "¡Correcto! (1/5 para subir)",
        }
        yield


# =============================================================================
# Helpers
# =============================================================================


def _create_iq_session(db, skill_id):
    """Create a fresh IQPracticeSession and return it."""
    iq = IQPracticeSession(skill_id=skill_id)
    db.add(iq)
    db.commit()
    db.refresh(iq)
    return iq


def _create_iq_round(db, iq_session, correct_answer="10"):
    """Create an IQ round with known values."""
    rnd = IQPracticeRound(
        session_id=iq_session.id,
        level=iq_session.level,
        puzzle_type="number_sequence",
        question="¿Qué número sigue? 2, 4, 6, 8, ?",
        options_json=json.dumps(["9", "10", "11", "12"]),
        correct_answer=correct_answer,
        explanation="La secuencia suma 2 cada vez.",
    )
    db.add(rnd)
    db.commit()
    db.refresh(rnd)
    return rnd


# =============================================================================
# iniciar_sesion
# =============================================================================


class TestIniciarSesion:
    """iq_practice_service.iniciar_sesion(db, skill_id)"""

    def test_iniciar_sesion_creates_session(self, session, skill_factory):
        """Verify session created with correct defaults."""
        skill = skill_factory(skill_type="iq_practice")

        iq = iq_practice_service.iniciar_sesion(session, skill.id)

        assert iq.id is not None
        assert iq.skill_id == skill.id
        assert iq.level == 1
        assert iq.best_level == 1
        assert iq.is_active is True
        assert iq.consecutive_correct == 0
        assert iq.consecutive_incorrect == 0
        assert iq.total_rounds == 0
        assert iq.consolidated_session_id is None

    def test_iniciar_sesion_invalid_skill(self, session):
        """Raises ValueError for bad skill_id."""
        with pytest.raises(ValueError, match="Skill not found"):
            iq_practice_service.iniciar_sesion(session, 99999)


# =============================================================================
# crear_round
# =============================================================================


class TestCrearRound:
    """iq_practice_service.crear_round(db, session_id)"""

    def test_crear_round_generates_puzzle(self, session, skill_factory):
        """Verify round created with AI-generated puzzle."""
        skill = skill_factory(skill_type="iq_practice")
        iq = iq_practice_service.iniciar_sesion(session, skill.id)

        round_obj, puzzle = iq_practice_service.crear_round(session, iq.id)

        assert round_obj.id is not None
        assert round_obj.session_id == iq.id
        assert round_obj.level == 1
        assert round_obj.puzzle_type == "number_sequence"
        assert round_obj.correct_answer == "10"
        assert json.loads(round_obj.options_json) == ["9", "10", "11", "12"]
        assert puzzle["question"] == "¿Qué número sigue? 2, 4, 6, 8, ?"

        # Session counter advanced
        session.refresh(iq)
        assert iq.total_rounds == 1

    def test_crear_round_invalid_session(self, session):
        """Raises ValueError for bad session_id."""
        with pytest.raises(ValueError, match="IQ session not found"):
            iq_practice_service.crear_round(session, 99999)

    def test_crear_round_closed_session(self, session, skill_factory):
        """Raises ValueError if session is already closed."""
        skill = skill_factory(skill_type="iq_practice")
        iq = iq_practice_service.iniciar_sesion(session, skill.id)
        iq.is_active = False
        session.add(iq)
        session.commit()

        with pytest.raises(ValueError, match="already closed"):
            iq_practice_service.crear_round(session, iq.id)


# =============================================================================
# enviar_intento
# =============================================================================


class TestEnviarIntento:
    """iq_practice_service.enviar_intento(db, round_id, user_answer)"""

    def test_enviar_intento_correct(self, session, skill_factory):
        """Correct answer returns correct=True."""
        skill = skill_factory(skill_type="iq_practice")
        iq = _create_iq_session(session, skill.id)
        rnd = _create_iq_round(session, iq)

        result = iq_practice_service.enviar_intento(session, rnd.id, "10")

        assert result["correct"] is True
        assert result["correct_answer"] is None  # not included when correct
        assert result["explanation"] == "La secuencia suma 2 cada vez."
        assert result["staircase_result"] is not None

    def test_enviar_intento_incorrect(self, session, skill_factory):
        """Incorrect answer returns correct=False and includes correct_answer."""
        skill = skill_factory(skill_type="iq_practice")
        iq = _create_iq_session(session, skill.id)
        rnd = _create_iq_round(session, iq, correct_answer="10")

        # Override evaluate_attempt to return False
        with patch("services.iq_practice_service.evaluate_attempt") as mock_eval:
            mock_eval.return_value = False
            result = iq_practice_service.enviar_intento(session, rnd.id, "12")

            assert result["correct"] is False
            assert result["correct_answer"] == "10"

    def test_enviar_intento_invalid_round(self, session):
        """Raises ValueError for bad round_id."""
        with pytest.raises(ValueError, match="Round not found"):
            iq_practice_service.enviar_intento(session, 99999, "10")

    def test_enviar_intento_updates_session(self, session, skill_factory):
        """Verify session fields updated after attempt."""
        skill = skill_factory(skill_type="iq_practice")
        iq = _create_iq_session(session, skill.id)
        rnd = _create_iq_round(session, iq)

        with patch("services.iq_practice_service.calculate_staircase") as mock_stair:
            mock_stair.return_value = {
                "new_level": 2,
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
                "level_changed": True,
                "message": "¡Pasaste al nivel 2!",
            }
            result = iq_practice_service.enviar_intento(session, rnd.id, "10")

            assert result["staircase_result"]["level_changed"] is True

            session.refresh(iq)
            assert iq.level == 2
            assert iq.best_level == 2


# =============================================================================
# consolidar_sesion
# =============================================================================


class TestConsolidarSesion:
    """iq_practice_service.consolidar_sesion(db, session_id, elapsed_seconds)"""

    def test_consolidar_sesion_minimum_rounds(self, session, skill_factory):
        """Raises ValueError if < 3 rounds."""
        skill = skill_factory(skill_type="iq_practice")
        iq = _create_iq_session(session, skill.id)
        iq.total_rounds = 2
        session.add(iq)
        session.commit()

        with pytest.raises(ValueError, match="Minimum 3 rounds required"):
            iq_practice_service.consolidar_sesion(session, iq.id, elapsed_seconds=60)

        session.refresh(iq)
        assert iq.is_active is True
        assert iq.consolidated_session_id is None

    def test_consolidar_sesion_creates_practice_session(self, session, skill_factory):
        """Verify consolidation creates PracticeSession and links correctly."""
        skill = skill_factory(skill_type="iq_practice")
        iq = _create_iq_session(session, skill.id)
        iq.total_rounds = 4
        iq.best_level = 3
        session.add(iq)
        session.commit()

        result = iq_practice_service.consolidar_sesion(session, iq.id, elapsed_seconds=120)

        assert result["status"] == "consolidated"
        assert result["practice_session_id"] is not None
        assert result["rounds_completed"] == 4
        assert result["best_level"] == 3

        # PracticeSession exists
        ps = session.get(PracticeSession, result["practice_session_id"])
        assert ps is not None
        assert ps.skill_id == skill.id
        session_data = json.loads(ps.session_data)
        assert session_data["type"] == "iq_practice"
        assert session_data["elapsed_seconds"] == 120
        assert session_data["best_level"] == 3

        # Atomic link
        session.refresh(iq)
        assert iq.is_active is False
        assert iq.consolidated_session_id == ps.id

    def test_consolidar_sesion_already_consolidated(self, session, skill_factory):
        """Raises ValueError if session already consolidated."""
        skill = skill_factory(skill_type="iq_practice")
        iq = _create_iq_session(session, skill.id)
        iq.total_rounds = 5
        iq.is_active = False
        session.add(iq)
        session.commit()

        with pytest.raises(ValueError, match="already consolidated"):
            iq_practice_service.consolidar_sesion(session, iq.id, elapsed_seconds=60)

    def test_consolidar_sesion_no_elapsed_seconds(self, session, skill_factory):
        """Consolidation works without elapsed_seconds."""
        skill = skill_factory(skill_type="iq_practice")
        iq = _create_iq_session(session, skill.id)
        iq.total_rounds = 3
        session.add(iq)
        session.commit()

        result = iq_practice_service.consolidar_sesion(session, iq.id, elapsed_seconds=None)

        assert result["status"] == "consolidated"
        ps = session.get(PracticeSession, result["practice_session_id"])
        session_data = json.loads(ps.session_data)
        assert "elapsed_seconds" not in session_data
