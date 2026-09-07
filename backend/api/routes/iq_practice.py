import json

from pydantic import BaseModel

from api.routes.game_base import GameRouter
from models.models import IQPracticeAttempt, IQPracticeRound, IQPracticeSession
from services import iq_practice_service


class IQSessionCreate(BaseModel):
    skill_id: int


class AttemptSubmission(BaseModel):
    user_answer: str


def _format_session(session):
    return {
        "id": session.id,
        "level": session.level,
        "is_active": session.is_active,
        "best_level": session.best_level,
    }


def _format_round(round_obj, puzzle):
    return {
        "id": round_obj.id,
        "question": round_obj.question,
        "options": json.loads(round_obj.options_json),
        "puzzle_type": round_obj.puzzle_type,
        "level": round_obj.level,
        "source": puzzle.get("source"),
    }


def _format_state(session):
    return {
        "level": session.level,
        "consecutive_correct": session.consecutive_correct,
        "consecutive_incorrect": session.consecutive_incorrect,
        "total_rounds": session.total_rounds,
        "is_active": session.is_active,
        "best_level": session.best_level,
    }


def _format_history_round(round_obj, attempts):
    return {
        "id": round_obj.id,
        "level": round_obj.level,
        "puzzle_type": round_obj.puzzle_type,
        "question": round_obj.question,
        "correct": any(a.correct for a in attempts) if attempts else None,
        "attempts": [
            {"correct": a.correct, "user_answer": a.user_answer}
            for a in attempts
        ],
    }


_game_router = GameRouter(
    prefix="",
    service=iq_practice_service,
    SessionModel=IQPracticeSession,
    RoundModel=IQPracticeRound,
    AttemptModel=IQPracticeAttempt,
    round_fk_field="session_id",
    session_create_body=IQSessionCreate,
    attempt_body=AttemptSubmission,
    format_session=_format_session,
    format_round=_format_round,
    create_round_extra=None,
    format_state=_format_state,
    format_history_round=_format_history_round,
    round_error_status=400,
    consolidate_error_status=400,
)

router = _game_router.router
