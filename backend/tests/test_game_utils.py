"""Tests for game_utils — shared utility functions for game services."""
from services.game_utils import consolidation_response


class TestConsolidationResponse:
    """game_utils.consolidation_response()"""

    def test_consolidation_response_basic(self):
        """Returns canonical consolidation response shape."""
        result = consolidation_response(
            practice_session_id=42,
            rounds_completed=5,
            summary={"best_level": 3},
        )

        assert result == {
            "status": "consolidated",
            "practice_session_id": 42,
            "rounds_completed": 5,
            "summary": {"best_level": 3},
        }

    def test_consolidation_response_full_summary(self):
        """Works with multiple summary fields."""
        result = consolidation_response(
            practice_session_id=100,
            rounds_completed=10,
            summary={
                "best_level": 7,
                "coaching_message": "¡Buen trabajo!",
                "accuracy": 0.85,
            },
        )

        assert result["status"] == "consolidated"
        assert result["practice_session_id"] == 100
        assert result["rounds_completed"] == 10
        assert result["summary"]["best_level"] == 7
        assert result["summary"]["coaching_message"] == "¡Buen trabajo!"

    def test_consolidation_response_zero_rounds(self):
        """Works with zero rounds (edge case)."""
        result = consolidation_response(
            practice_session_id=1,
            rounds_completed=0,
            summary={},
        )

        assert result["rounds_completed"] == 0
        assert result["summary"] == {}

    def test_consolidation_response_large_ids(self):
        """Works with large practice_session_id values."""
        result = consolidation_response(
            practice_session_id=999999,
            rounds_completed=25,
            summary={"message": "test"},
        )

        assert result["practice_session_id"] == 999999
