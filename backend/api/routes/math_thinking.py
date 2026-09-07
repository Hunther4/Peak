
from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session

from api.routes.game_base import GameRouter
from core.database import get_session
from core.limiter import get_rate_limit_str, limiter
from models.models import MathThinkingAttempt, MathThinkingRound, MathThinkingSession
from services import math_thinking_service


class MathSessionCreate(BaseModel):
    skill_id: int


class AttemptSubmission(BaseModel):
    user_answer: float


def _format_session(session):
    return {
        "id": session.id,
        "level": session.level,
        "is_active": session.is_active,
        "best_level": session.best_level,
    }


def _format_round(round_obj, problem):
    return {
        "id": round_obj.id,
        "problem_text": round_obj.problem_text,
        "level": round_obj.level,
        "source": problem.get("source"),
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
        "problem_text": round_obj.problem_text,
        "correct": any(a.correct for a in attempts) if attempts else None,
        "attempts": [
            {"correct": a.correct, "user_answer": a.user_answer}
            for a in attempts
        ],
    }


_game_router = GameRouter(
    prefix="",
    service=math_thinking_service,
    SessionModel=MathThinkingSession,
    RoundModel=MathThinkingRound,
    AttemptModel=MathThinkingAttempt,
    round_fk_field="session_id",
    session_create_body=MathSessionCreate,
    attempt_body=AttemptSubmission,
    format_session=_format_session,
    format_round=_format_round,
    create_round_extra=None,
    format_state=_format_state,
    format_history_round=_format_history_round,
    round_error_status=400,
    consolidate_error_status=400,
    always_use_error_status=True,
)

router = _game_router.router


@router.get("/rounds/{round_id}/hint")
@limiter.limit(get_rate_limit_str())
def get_hint(request: Request, round_id: int, db: Session = Depends(get_session)):
    """Get an AI-generated hint for the current math problem."""
    try:
        return math_thinking_service.get_hint(db, round_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
