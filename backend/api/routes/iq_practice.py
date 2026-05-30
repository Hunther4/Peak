from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
import json
import yaml
from typing import Optional
from pydantic import BaseModel

import os

from core.database import engine
from core.iq_practice import generate_puzzle, evaluate_attempt, calculate_staircase, IQPuzzle
from core import router as core_router
from models.models import Skill, IQPracticeSession, IQPracticeRound, IQPracticeAttempt
from models.models import Session as PracticeSession

router = APIRouter()


class IQSessionCreate(BaseModel):
    skill_id: int


class AttemptSubmission(BaseModel):
    user_answer: str


def get_db():
    with Session(engine) as session:
        yield session


def load_skill_config():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(base_dir, "skills", "iq-practice.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)


@router.post("/sessions")
def create_iq_session(body: IQSessionCreate, db: Session = Depends(get_db)):
    """Start a new IQ Practice session."""
    skill = db.get(Skill, body.skill_id)
    if not skill:
        raise HTTPException(404, "Skill not found")
    session = IQPracticeSession(skill_id=body.skill_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "id": session.id,
        "level": session.level,
        "is_active": session.is_active,
        "best_level": session.best_level,
    }


@router.post("/sessions/{session_id}/rounds")
def create_round(session_id: int, db: Session = Depends(get_db)):
    """Generate a new IQ puzzle using AI based on current session level."""
    iq_session = db.get(IQPracticeSession, session_id)
    if not iq_session:
        raise HTTPException(404, "IQ session not found")
    if not iq_session.is_active:
        raise HTTPException(400, "IQ session is already closed")

    config = load_skill_config()
    puzzle = generate_puzzle(
        iq_session.level,
        config,
        core_router.execute_with_router,
    )

    round_obj = IQPracticeRound(
        session_id=session_id,
        level=iq_session.level,
        puzzle_type=puzzle["puzzle_type"],
        question=puzzle["question"],
        options_json=json.dumps(puzzle["options"]),
        correct_answer=puzzle["correct_answer"],
        explanation=puzzle["explanation"],
    )
    db.add(round_obj)

    iq_session.total_rounds += 1
    db.add(iq_session)

    db.commit()
    db.refresh(round_obj)

    return {
        "id": round_obj.id,
        "question": round_obj.question,
        "options": json.loads(round_obj.options_json),
        "puzzle_type": round_obj.puzzle_type,
        "level": round_obj.level,
    }


@router.post("/rounds/{round_id}/attempts")
def submit_attempt(
    round_id: int,
    body: AttemptSubmission,
    db: Session = Depends(get_db),
):
    """Submit an answer and get feedback with staircase update."""
    round_obj = db.get(IQPracticeRound, round_id)
    if not round_obj:
        raise HTTPException(404, "Round not found")

    iq_session = db.get(IQPracticeSession, round_obj.session_id)
    if not iq_session:
        raise HTTPException(404, "Session not found")

    correct = evaluate_attempt(body.user_answer, round_obj.correct_answer)

    staircase_result = calculate_staircase(
        iq_session.level,
        correct,
        iq_session.consecutive_correct,
        iq_session.consecutive_incorrect,
    )

    attempt = IQPracticeAttempt(
        round_id=round_id,
        user_answer=body.user_answer,
        correct=correct,
    )
    db.add(attempt)

    # Update session staircase
    iq_session.level = staircase_result["new_level"]
    iq_session.consecutive_correct = staircase_result["new_consecutive_correct"]
    iq_session.consecutive_incorrect = staircase_result["new_consecutive_incorrect"]

    if iq_session.level > iq_session.best_level:
        iq_session.best_level = iq_session.level

    db.add(iq_session)
    db.commit()
    db.refresh(attempt)

    return {
        "correct": correct,
        "correct_answer": round_obj.correct_answer if not correct else None,
        "explanation": round_obj.explanation,
        "staircase_result": staircase_result,
    }


@router.post("/sessions/{session_id}/consolidate")
def consolidate_session(session_id: int, db: Session = Depends(get_db)):
    """Close an IQ Practice session and create a PracticeSession for timeline."""
    iq_session = db.get(IQPracticeSession, session_id)
    if not iq_session:
        raise HTTPException(404, "IQ session not found")
    if not iq_session.is_active:
        raise HTTPException(400, "Session already consolidated")
    if iq_session.total_rounds < 3:
        raise HTTPException(400, "Minimum 3 puzzles required before consolidation")

    iq_session.is_active = False

    session_data = {
        "type": "iq_practice",
        "total_rounds": iq_session.total_rounds,
        "best_level": iq_session.best_level,
        "final_level": iq_session.level,
    }

    practice_session = PracticeSession(
        skill_id=iq_session.skill_id,
        what_i_practiced=f"Práctica de IQ — Nivel {iq_session.level}",
        micro_error_found=f"IQ session: {iq_session.total_rounds} puzzles, best level {iq_session.best_level}",
        difficulty=3,
        entry_mode="quick",
        duration_minutes=max(10, iq_session.total_rounds * 2),
        session_data=json.dumps(session_data),
    )
    db.add(practice_session)
    db.commit()
    db.refresh(practice_session)

    iq_session.consolidated_session_id = practice_session.id
    db.add(iq_session)
    db.commit()

    return {
        "status": "consolidated",
        "practice_session_id": practice_session.id,
        "rounds_completed": iq_session.total_rounds,
        "best_level": iq_session.best_level,
    }


@router.get("/sessions/{session_id}/state")
def get_session_state(session_id: int, db: Session = Depends(get_db)):
    """Get current IQ Practice session state."""
    iq_session = db.get(IQPracticeSession, session_id)
    if not iq_session:
        raise HTTPException(404, "IQ session not found")

    return {
        "level": iq_session.level,
        "consecutive_correct": iq_session.consecutive_correct,
        "consecutive_incorrect": iq_session.consecutive_incorrect,
        "total_rounds": iq_session.total_rounds,
        "is_active": iq_session.is_active,
        "best_level": iq_session.best_level,
    }


@router.get("/sessions/{session_id}/history")
def get_round_history(session_id: int, db: Session = Depends(get_db)):
    """Get all rounds and attempts for an IQ Practice session."""
    iq_session = db.get(IQPracticeSession, session_id)
    if not iq_session:
        raise HTTPException(404, "IQ session not found")

    rounds = db.exec(
        select(IQPracticeRound)
        .where(IQPracticeRound.session_id == session_id)
        .order_by(IQPracticeRound.created_at)
    ).all()

    result = []
    for r in rounds:
        attempts = db.exec(
            select(IQPracticeAttempt)
            .where(IQPracticeAttempt.round_id == r.id)
            .order_by(IQPracticeAttempt.created_at)
        ).all()

        result.append({
            "id": r.id,
            "level": r.level,
            "puzzle_type": r.puzzle_type,
            "question": r.question,
            "correct": any(a.correct for a in attempts) if attempts else None,
            "attempts": [
                {
                    "correct": a.correct,
                    "user_answer": a.user_answer,
                }
                for a in attempts
            ],
        })

    return {"rounds": result, "total": len(result)}
