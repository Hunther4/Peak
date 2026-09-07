from typing import List, Optional

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session

from api.routes.game_base import GameRouter
from core.database import get_session
from core.limiter import get_rate_limit_str, limiter
from core.memory_number import get_phase_config
from models.models import MemoryNumberAttempt, MemoryNumberRound, MemoryNumberSession
from services import memory_game_service


class GameSessionCreate(BaseModel):
    skill_id: int


class AttemptSubmission(BaseModel):
    submitted_numbers: List[int]


class StrategyLogPayload(BaseModel):
    strategy_used: str


class SessionMetaPayload(BaseModel):
    strategy_type: str
    self_reported_difficulty: Optional[int] = None
    notes: Optional[str] = None


def _format_session(session):
    return {
        "id": session.id,
        "phase": session.phase,
        "current_span": session.current_span,
        "best_span": session.best_span,
        "best_phase": session.best_phase,
        "timing": get_phase_config(session.phase)["timing"],
    }


def _format_round(round_obj, extra):
    numbers, phase_config = extra
    return {
        "id": round_obj.id,
        "phase": round_obj.phase,
        "span": round_obj.span,
        "length": round_obj.sequence_length,
        "timing": phase_config["timing"],
        "numbers": numbers,
    }


def _format_state(session):
    return {
        "phase": session.phase,
        "current_span": session.current_span,
        "consecutive_correct": session.consecutive_correct,
        "consecutive_incorrect": session.consecutive_incorrect,
        "best_span": session.best_span,
        "best_phase": session.best_phase,
        "total_rounds": session.total_rounds,
        "is_active": session.is_active,
        "timing": get_phase_config(session.phase)["timing"],
    }


def _format_history_round(round_obj, attempts):
    return {
        "id": round_obj.id,
        "phase": round_obj.phase,
        "span": round_obj.span,
        "correct": any(a.correct for a in attempts) if attempts else None,
        "attempts": [
            {
                "correct": a.correct,
                "correct_positions": a.correct_positions,
                "total_positions": a.total_positions,
            }
            for a in attempts
        ],
    }


_game_router = GameRouter(
    prefix="",
    service=memory_game_service,
    SessionModel=MemoryNumberSession,
    RoundModel=MemoryNumberRound,
    AttemptModel=MemoryNumberAttempt,
    round_fk_field="game_session_id",
    session_create_body=GameSessionCreate,
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


@router.post("/rounds/{round_id}/strategy-log")
@limiter.limit(get_rate_limit_str())
def log_round_strategy(
    request: Request,
    round_id: int,
    body: StrategyLogPayload,
    db: Session = Depends(get_session),
):
    """Record per-round strategy after attempt submission."""
    try:
        return memory_game_service.log_round_strategy(db, round_id, body.strategy_used)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/sessions/{session_id}/meta")
@limiter.limit(get_rate_limit_str())
def save_session_meta(
    request: Request,
    session_id: int,
    body: SessionMetaPayload,
    db: Session = Depends(get_session),
):
    """Persist session-level strategy + self-reported difficulty + notes."""
    try:
        return memory_game_service.save_session_meta(
            db, session_id, body.strategy_type,
            body.self_reported_difficulty, body.notes,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
