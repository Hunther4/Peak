"""
Direct tests for game_base shared functions.

Tests the common session initialization and consolidation logic
used by memory, math, and IQ game services.
"""
import json
from unittest.mock import ANY, patch

import pytest

from models.models import MemoryNumberSession
from models.models import Session as PracticeSession
from services.game_base import consolidar_sesion_base, iniciar_sesion_base

# =============================================================================
# iniciar_sesion_base
# =============================================================================


class TestIniciarSesionBase:
    """game_base.iniciar_sesion_base(db, SessionModel, skill_id)"""

    def test_iniciar_sesion_base_creates_session(self, session, skill_factory):
        """Verify session created with correct FK."""
        skill = skill_factory(skill_type="memory_number")

        result = iniciar_sesion_base(session, MemoryNumberSession, skill.id)

        assert result.id is not None
        assert result.skill_id == skill.id
        assert result.is_active is True

    def test_iniciar_sesion_base_invalid_skill(self, session):
        """Raises ValueError for bad skill_id."""
        with pytest.raises(ValueError, match="Skill not found"):
            iniciar_sesion_base(session, MemoryNumberSession, 99999)

    def test_iniciar_sesion_base_returns_correct_model(self, session, skill_factory):
        """Returns an instance of the passed SessionModel."""
        skill = skill_factory(skill_type="memory_number")

        result = iniciar_sesion_base(session, MemoryNumberSession, skill.id)

        assert isinstance(result, MemoryNumberSession)

    def test_iniciar_sesion_base_commits_to_db(self, session, skill_factory):
        """Session is persisted in the database."""
        skill = skill_factory(skill_type="memory_number")

        result = iniciar_sesion_base(session, MemoryNumberSession, skill.id)

        # Re-fetch from DB
        fetched = session.get(MemoryNumberSession, result.id)
        assert fetched is not None
        assert fetched.skill_id == skill.id


# =============================================================================
# consolidar_sesion_base
# =============================================================================


class TestConsolidarSesionBase:
    """game_base.consolidar_sesion_base(db, SessionModel, session_id, ...)"""

    def _build_session_data(self, gs):
        return {
            "type": "test_game",
            "total_rounds": gs.total_rounds,
        }

    def _build_practice_fields(self, gs):
        return {
            "skill_id": gs.skill_id,
            "what_i_practiced": f"Test Game — {gs.total_rounds} rounds",
            "micro_error_found": f"Test session: {gs.total_rounds} rounds",
            "difficulty": 3,
            "entry_mode": "quick",
            "duration_minutes": max(10, gs.total_rounds * 2),
        }

    def test_consolidar_sesion_base_minimum_rounds(self, session, skill_factory):
        """Raises ValueError if < min_rounds (default 3)."""
        skill = skill_factory(skill_type="memory_number")
        game_session = MemoryNumberSession(skill_id=skill.id)
        game_session.total_rounds = 2
        session.add(game_session)
        session.commit()

        with pytest.raises(ValueError, match="Minimum 3 rounds required"):
            consolidar_sesion_base(
                session, MemoryNumberSession, game_session.id,
                elapsed_seconds=60, game_name="Test",
                build_session_data=self._build_session_data,
                build_practice_fields=self._build_practice_fields,
            )

    def test_consolidar_sesion_base_custom_min_rounds(self, session, skill_factory):
        """Raises ValueError with custom min_rounds_message."""
        skill = skill_factory(skill_type="memory_number")
        game_session = MemoryNumberSession(skill_id=skill.id)
        game_session.total_rounds = 1
        session.add(game_session)
        session.commit()

        with pytest.raises(ValueError, match="Need at least 5 test rounds"):
            consolidar_sesion_base(
                session, MemoryNumberSession, game_session.id,
                elapsed_seconds=60, game_name="Test",
                build_session_data=self._build_session_data,
                build_practice_fields=self._build_practice_fields,
                min_rounds=5,
                min_rounds_message="Need at least 5 test rounds",
            )

    def test_consolidar_sesion_base_not_found(self, session):
        """Raises ValueError for bad session_id."""
        with pytest.raises(ValueError, match="Test session not found"):
            consolidar_sesion_base(
                session, MemoryNumberSession, 99999,
                elapsed_seconds=60, game_name="Test",
                build_session_data=self._build_session_data,
                build_practice_fields=self._build_practice_fields,
            )

    def test_consolidar_sesion_base_already_consolidated(self, session, skill_factory):
        """Raises ValueError if session is not active."""
        skill = skill_factory(skill_type="memory_number")
        game_session = MemoryNumberSession(skill_id=skill.id, is_active=False)
        game_session.total_rounds = 5
        session.add(game_session)
        session.commit()

        with pytest.raises(ValueError, match="already consolidated"):
            consolidar_sesion_base(
                session, MemoryNumberSession, game_session.id,
                elapsed_seconds=60, game_name="Test",
                build_session_data=self._build_session_data,
                build_practice_fields=self._build_practice_fields,
            )

    def test_consolidar_sesion_base_creates_practice_session(
        self, session, skill_factory,
    ):
        """Verify PracticeSession created and game session linked."""
        skill = skill_factory(skill_type="memory_number")
        game_session = MemoryNumberSession(skill_id=skill.id)
        game_session.total_rounds = 4
        session.add(game_session)
        session.commit()

        practice_session, gs = consolidar_sesion_base(
            session, MemoryNumberSession, game_session.id,
            elapsed_seconds=120, game_name="Test",
            build_session_data=self._build_session_data,
            build_practice_fields=self._build_practice_fields,
        )

        assert isinstance(practice_session, PracticeSession)
        assert practice_session.skill_id == skill.id
        assert practice_session.entry_mode == "quick"
        assert practice_session.duration_minutes >= 10

        session_data = json.loads(practice_session.session_data)
        assert session_data["type"] == "test_game"
        assert session_data["elapsed_seconds"] == 120

        # Game session is deactivated and linked
        assert gs.is_active is False
        assert gs.consolidated_session_id == practice_session.id

    def test_consolidar_sesion_base_no_elapsed_seconds(
        self, session, skill_factory,
    ):
        """Elapsed seconds not included when None."""
        skill = skill_factory(skill_type="memory_number")
        game_session = MemoryNumberSession(skill_id=skill.id)
        game_session.total_rounds = 3
        session.add(game_session)
        session.commit()

        practice_session, gs = consolidar_sesion_base(
            session, MemoryNumberSession, game_session.id,
            elapsed_seconds=None, game_name="Test",
            build_session_data=self._build_session_data,
            build_practice_fields=self._build_practice_fields,
        )

        session_data = json.loads(practice_session.session_data)
        assert "elapsed_seconds" not in session_data

    def test_consolidar_sesion_base_applies_staircase(
        self, session, skill_factory,
    ):
        """Verify staircase is applied during consolidation."""
        skill = skill_factory(skill_type="memory_number")
        game_session = MemoryNumberSession(skill_id=skill.id)
        game_session.total_rounds = 4
        # Set consecutive values so determine_session_success returns bool
        game_session.consecutive_correct = 2
        game_session.consecutive_incorrect = 0
        session.add(game_session)
        session.commit()

        with patch("services.staircase.apply_staircase") as mock_apply:
            practice_session, gs = consolidar_sesion_base(
                session, MemoryNumberSession, game_session.id,
                elapsed_seconds=60, game_name="Test",
                build_session_data=self._build_session_data,
                build_practice_fields=self._build_practice_fields,
            )

            mock_apply.assert_called_once_with(
                ANY, skill, True,
                trigger="session_consolidation",
                session_id=practice_session.id,
            )
