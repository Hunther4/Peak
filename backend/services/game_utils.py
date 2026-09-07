"""Shared utilities for game services."""
from typing import Any


def consolidation_response(
    practice_session_id: int,
    rounds_completed: int,
    summary: dict[str, Any],
) -> dict:
    """Canonical consolidation response envelope.

    All game consolidation endpoints MUST return this shape.
    The ``summary`` field is game-specific and may contain any
    game-relevant data (best_level, coaching_message, etc.).

    Example::

        return consolidation_response(
            practice_session_id=42,
            rounds_completed=5,
            summary={"best_level": 3, "coaching_message": "..."},
        )
    """
    return {
        "status": "consolidated",
        "practice_session_id": practice_session_id,
        "rounds_completed": rounds_completed,
        "summary": summary,
    }
