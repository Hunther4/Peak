"""
Direct service-layer tests for memory_game_service.

Bypasses the FastAPI HTTP layer to validate the service functions in
isolation. Catches logic bugs without going through routing, validation,
or middleware (auth, rate limit, etc.).
"""
import json
from unittest.mock import patch

import pytest

from models.models import MemoryNumberRound, MemoryNumberSession
from models.models import Session as PracticeSession
from services import memory_game_service

# =============================================================================
# AI mock (autouse) — service depends on generate_numbers, evaluate_attempt,
# calculate_staircase, get_phase_config, and AI coaching
# =============================================================================


@pytest.fixture(autouse=True)
def mock_memory_game_deps():
    """Mock AI-dependent and core functions so tests run offline."""
    with (
        patch("services.memory_game_service.generate_numbers") as mock_gen,
        patch("services.memory_game_service.get_phase_config") as mock_phase,
        patch("services.memory_game_service.evaluate_attempt") as mock_eval,
        patch("services.memory_game_service.calculate_staircase") as mock_stair,
        patch("services.memory_game_service.core_router.execute_with_router") as mock_ai,
        patch("services.memory_game_service.record_error"),
    ):
        # Default: phase config for phase 1
        mock_phase.return_value = {"digit_max": 1, "ai_assisted": False, "timing": 5}

        # Default: generate_numbers returns a simple list
        mock_gen.return_value = [4, 8, 5, 3]

        # Default: evaluate_attempt returns correct=True
        mock_eval.return_value = {
            "correct": True,
            "correct_positions": 4,
            "total_positions": 4,
            "errors": [],
        }

        # Default: calculate_staircase - span stays same, no phase change
        mock_stair.return_value = {
            "new_span": 4,
            "new_phase": 1,
            "phase_changed": False,
            "message": "Correcto!",
            "new_consecutive_correct": 1,
            "new_consecutive_incorrect": 0,
        }

        # Default: AI coaching returns a message
        class FakeCoaching:
            coaching_message = "¡Buen trabajo! Probá agrupar de a 3."

        mock_ai.return_value = FakeCoaching()

        yield


# =============================================================================
# Helpers
# =============================================================================


def _create_mem_session(db, skill_id):
    """Create a fresh MemoryNumberSession and return it."""
    mem = MemoryNumberSession(skill_id=skill_id)
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem


def _create_mem_round(db, mem_session, span=4, phase=1):
    """Create a round with known values."""
    rnd = MemoryNumberRound(
        game_session_id=mem_session.id,
        phase=phase,
        span=span,
        digit_max=1,
        numbers_json=json.dumps([4, 8, 5, 3]),
        sequence_length=4,
        ai_assisted=False,
    )
    db.add(rnd)
    db.commit()
    db.refresh(rnd)
    return rnd


# =============================================================================
# iniciar_sesion
# =============================================================================


class TestIniciarSesion:
    """memory_game_service.iniciar_sesion(db, skill_id)"""

    def test_iniciar_sesion_creates_session(self, session, skill_factory):
        """Verify session created with correct defaults."""
        skill = skill_factory(skill_type="memory_number")

        mem = memory_game_service.iniciar_sesion(session, skill.id)

        assert mem.id is not None
        assert mem.skill_id == skill.id
        assert mem.phase == 1
        assert mem.current_span == 4
        assert mem.is_active is True
        assert mem.consecutive_correct == 0
        assert mem.consecutive_incorrect == 0
        assert mem.total_rounds == 0
        assert mem.best_span == 4
        assert mem.best_phase == 1
        assert mem.consolidated_session_id is None

    def test_iniciar_sesion_invalid_skill(self, session):
        """Raises ValueError for bad skill_id."""
        with pytest.raises(ValueError, match="Skill not found"):
            memory_game_service.iniciar_sesion(session, 99999)


# =============================================================================
# crear_round
# =============================================================================


class TestCrearRound:
    """memory_game_service.crear_round(db, session_id) -> (round, extra_tuple)"""

    def test_crear_round_creates_round(self, session, skill_factory):
        """Verify round created and session counters updated."""
        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)

        round_obj, extra = memory_game_service.crear_round(session, mem.id)

        assert round_obj.id is not None
        assert round_obj.game_session_id == mem.id
        assert round_obj.span == 4
        assert round_obj.phase == 1
        assert json.loads(round_obj.numbers_json) == [4, 8, 5, 3]
        assert round_obj.sequence_length == 4

        # Extra tuple contains (numbers, phase_config)
        assert isinstance(extra, tuple)
        assert extra[0] == [4, 8, 5, 3]
        assert extra[1] == {"digit_max": 1, "ai_assisted": False, "timing": 5}

        # Session counter advanced
        session.refresh(mem)
        assert mem.total_rounds == 1

    def test_crear_round_inactive_session(self, session, skill_factory):
        """Raises ValueError if session is not active."""
        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)
        mem.is_active = False
        session.add(mem)
        session.commit()

        with pytest.raises(ValueError, match="already closed"):
            memory_game_service.crear_round(session, mem.id)

    def test_crear_round_invalid_session(self, session):
        """Raises ValueError for bad session_id."""
        with pytest.raises(ValueError, match="Game session not found"):
            memory_game_service.crear_round(session, 99999)


# =============================================================================
# enviar_intento
# =============================================================================


class TestEnviarIntento:
    """memory_game_service.enviar_intento(db, round_id, submitted_numbers)"""

    def test_enviar_intento_correct(self, session, skill_factory):
        """Correct attempt returns evaluation result."""
        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)
        rnd = _create_mem_round(session, mem)

        result = memory_game_service.enviar_intento(session, rnd.id, [4, 8, 5, 3])

        assert result["correct"] is True
        assert result["correct_positions"] == 4
        assert result["total_positions"] == 4
        assert result["staircase_result"] is not None
        assert "next_timing" in result

        # Attempt row created
        from models.models import MemoryNumberAttempt
        attempts = session.exec(
            __import__("sqlmodel").select(MemoryNumberAttempt).where(
                MemoryNumberAttempt.round_id == rnd.id
            )
        ).all()
        assert len(attempts) == 1
        assert attempts[0].correct is True

    def test_enviar_intento_invalid_round(self, session):
        """Raises ValueError for bad round_id."""
        with pytest.raises(ValueError, match="Round not found"):
            memory_game_service.enviar_intento(session, 99999, [1, 2, 3, 4])

    def test_enviar_intento_updates_staircase(self, session, skill_factory):
        """Verify staircase result is applied to the session."""
        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)
        rnd = _create_mem_round(session, mem)

        # The mock calculate_staircase returns span=4 still, but we check
        # the session was passed through the call
        with patch("services.memory_game_service.calculate_staircase") as mock_stair:
            mock_stair.return_value = {
                "new_span": 5,
                "new_phase": 1,
                "phase_changed": False,
                "message": "¡3 aciertos seguidos! Span sube a 5",
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
            }
            result = memory_game_service.enviar_intento(session, rnd.id, [4, 8, 5, 3])

            assert result["staircase_result"]["new_span"] == 5
            session.refresh(mem)
            assert mem.current_span == 5
            assert mem.best_span == 5


# =============================================================================
# consolidar_sesion
# =============================================================================


class TestConsolidarSesion:
    """memory_game_service.consolidar_sesion(db, session_id, elapsed_seconds)"""

    def test_consolidar_sesion_minimum_rounds(self, session, skill_factory):
        """Raises ValueError if < 3 rounds."""
        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)
        mem.total_rounds = 2
        session.add(mem)
        session.commit()

        with pytest.raises(ValueError, match="Minimum 3 rounds required"):
            memory_game_service.consolidar_sesion(session, mem.id, elapsed_seconds=60)

        # Session must remain active after the failed attempt
        session.refresh(mem)
        assert mem.is_active is True
        assert mem.consolidated_session_id is None

    def test_consolidar_sesion_creates_practice_session(self, session, skill_factory):
        """Verify consolidation creates PracticeSession and links correctly."""
        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)
        mem.total_rounds = 5
        mem.best_span = 6
        mem.best_phase = 2
        session.add(mem)
        session.commit()

        result = memory_game_service.consolidar_sesion(session, mem.id, elapsed_seconds=120)

        assert result["status"] == "consolidated"
        assert result["practice_session_id"] is not None
        assert result["rounds_completed"] == 5
        assert result["best_span"] == 6

        # PracticeSession exists
        ps = session.get(PracticeSession, result["practice_session_id"])
        assert ps is not None
        assert ps.skill_id == skill.id
        session_data = json.loads(ps.session_data)
        assert session_data["type"] == "memory_number"
        assert session_data["elapsed_seconds"] == 120
        assert session_data["best_span"] == 6

        # Atomic link
        session.refresh(mem)
        assert mem.is_active is False
        assert mem.consolidated_session_id == ps.id

    def test_consolidar_sesion_already_consolidated(self, session, skill_factory):
        """Raises ValueError if session already consolidated."""
        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)
        mem.total_rounds = 5
        mem.is_active = False  # already deactivated
        session.add(mem)
        session.commit()

        with pytest.raises(ValueError, match="already consolidated"):
            memory_game_service.consolidar_sesion(session, mem.id, elapsed_seconds=60)

    def test_consolidar_sesion_no_elapsed(self, session, skill_factory):
        """Consolidation works without elapsed_seconds."""
        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)
        mem.total_rounds = 4
        session.add(mem)
        session.commit()

        result = memory_game_service.consolidar_sesion(session, mem.id, elapsed_seconds=None)

        assert result["status"] == "consolidated"
        ps = session.get(PracticeSession, result["practice_session_id"])
        session_data = json.loads(ps.session_data)
        assert "elapsed_seconds" not in session_data


# =============================================================================
# log_round_strategy
# =============================================================================


class TestLogRoundStrategy:
    """memory_game_service.log_round_strategy(db, round_id, strategy_used)"""

    def test_log_round_strategy_creates_log(self, session, skill_factory):
        """Verify MemoryStrategyLog is created."""
        from models.cognitive_models import MemoryStrategyLog
        from models.models import MemoryNumberAttempt

        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)
        rnd = _create_mem_round(session, mem)

        # Add an attempt so effective=True
        attempt = MemoryNumberAttempt(
            round_id=rnd.id,
            submitted_numbers_json=json.dumps([4, 8, 5, 3]),
            correct=True,
            correct_positions=4,
            total_positions=4,
        )
        session.add(attempt)
        session.commit()

        result = memory_game_service.log_round_strategy(session, rnd.id, "chunking")

        assert result["id"] is not None
        assert result["effective"] is True

        log = session.get(MemoryStrategyLog, result["id"])
        assert log is not None
        assert log.strategy_used == "chunking"
        assert log.span_at_attempt == 4

    def test_log_round_strategy_invalid_round(self, session):
        """Raises ValueError for bad round_id."""
        with pytest.raises(ValueError, match="Round not found"):
            memory_game_service.log_round_strategy(session, 99999, "chunking")


# =============================================================================
# save_session_meta
# =============================================================================


class TestSaveSessionMeta:
    """memory_game_service.save_session_meta(db, session_id, ...)"""

    def test_save_session_meta_creates_meta(self, session, skill_factory):
        """Verify MemorySessionMeta is created."""
        from models.cognitive_models import MemorySessionMeta

        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)

        result = memory_game_service.save_session_meta(
            session, mem.id,
            strategy_type="chunking",
            self_reported_difficulty=3,
            notes="Usé chunking de a 3",
        )

        assert result["id"] is not None
        assert result["strategy_type"] == "chunking"
        assert result["self_reported_difficulty"] == 3

        meta = session.get(MemorySessionMeta, result["id"])
        assert meta is not None
        assert meta.notes == "Usé chunking de a 3"

    def test_save_session_meta_invalid_session(self, session):
        """Raises ValueError for bad session_id."""
        with pytest.raises(ValueError, match="Game session not found"):
            memory_game_service.save_session_meta(
                session, 99999,
                strategy_type="chunking",
                self_reported_difficulty=3,
                notes=None,
            )

    def test_save_session_meta_invalid_difficulty(self, session, skill_factory):
        """Raises ValueError for difficulty outside 1-5."""
        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)

        with pytest.raises(ValueError, match="difficulty must be 1-5"):
            memory_game_service.save_session_meta(
                session, mem.id,
                strategy_type="chunking",
                self_reported_difficulty=6,
                notes=None,
            )

    def test_save_session_meta_none_difficulty(self, session, skill_factory):
        """None difficulty is valid."""
        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)

        result = memory_game_service.save_session_meta(
            session, mem.id,
            strategy_type="rehearsal",
            self_reported_difficulty=None,
            notes=None,
        )
        assert result["self_reported_difficulty"] is None


# =============================================================================
# get_phase_config usage (verify the service uses it correctly)
# =============================================================================


class TestGetPhaseConfigUsage:
    """Verify get_phase_config is called during crear_round and consolidar_sesion."""

    def test_crear_round_uses_phase_config(self, session, skill_factory, mock_memory_game_deps):
        """Verify get_phase_config is called with the session's phase."""

        skill = skill_factory(skill_type="memory_number")
        mem = _create_mem_session(session, skill.id)

        with patch("services.memory_game_service.get_phase_config") as mock_phase:
            mock_phase.return_value = {"digit_max": 1, "ai_assisted": False, "timing": 5}
            with patch("services.memory_game_service.generate_numbers") as mock_gen:
                mock_gen.return_value = [4, 8, 5, 3]

                memory_game_service.crear_round(session, mem.id)

                mock_phase.assert_called_once_with(1)  # phase=1 for new session
