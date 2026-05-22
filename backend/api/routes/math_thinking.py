from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
import json
import yaml
from typing import Optional
from pydantic import BaseModel

from core.database import engine
from core.math_thinking import generate_problem, evaluate_attempt, calculate_staircase, MathProblem
from core import router as core_router
from models.models import Skill, MathThinkingSession, MathThinkingRound, MathThinkingAttempt
from models.models import Session as PracticeSession

router = APIRouter()


class AttemptSubmission(BaseModel):
    user_answer: float


def get_db():
    with Session(engine) as session:
        yield session


def load_skill_config():
    with open("skills/math-thinking.yaml") as f:
        return yaml.safe_load(f)


@router.post("/sessions")
def create_math_session(skill_id: int, db: Session = Depends(get_db)):
    """Start a new math thinking session."""
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(404, "Skill not found")
    session = MathThinkingSession(skill_id=skill_id)
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
    """Generate a new math problem using AI based on current session level."""
    mt_session = db.get(MathThinkingSession, session_id)
    if not mt_session:
        raise HTTPException(404, "Math session not found")
    if not mt_session.is_active:
        raise HTTPException(400, "Math session is already closed")

    config = load_skill_config()
    problem = generate_problem(
        mt_session.level,
        config,
        core_router.execute_with_router,
    )

    round_obj = MathThinkingRound(
        session_id=session_id,
        level=mt_session.level,
        problem_text=problem["question"],
        correct_answer=problem["correct_answer"],
        solution_steps_json=json.dumps(problem["solution_steps"]),
    )
    db.add(round_obj)

    mt_session.total_rounds += 1
    db.add(mt_session)

    db.commit()
    db.refresh(round_obj)

    return {
        "id": round_obj.id,
        "problem_text": round_obj.problem_text,
        "level": round_obj.level,
    }


@router.post("/rounds/{round_id}/attempts")
def submit_attempt(
    round_id: int,
    body: AttemptSubmission,
    db: Session = Depends(get_db),
):
    """Submit an answer and get feedback with staircase update."""
    round_obj = db.get(MathThinkingRound, round_id)
    if not round_obj:
        raise HTTPException(404, "Round not found")

    mt_session = db.get(MathThinkingSession, round_obj.session_id)
    if not mt_session:
        raise HTTPException(404, "Session not found")

    correct = evaluate_attempt(body.user_answer, round_obj.correct_answer)

    staircase_result = calculate_staircase(
        mt_session.level,
        correct,
        mt_session.consecutive_correct,
        mt_session.consecutive_incorrect,
    )

    # Return pre-generated solution steps on error only
    solution_steps_json = (
        round_obj.solution_steps_json if not correct else None
    )

    attempt = MathThinkingAttempt(
        round_id=round_id,
        user_answer=body.user_answer,
        correct=correct,
        solution_steps_json=solution_steps_json,
    )
    db.add(attempt)

    # Update session with new staircase state
    mt_session.level = staircase_result["new_level"]
    mt_session.consecutive_correct = staircase_result["new_consecutive_correct"]
    mt_session.consecutive_incorrect = staircase_result["new_consecutive_incorrect"]

    if mt_session.level > mt_session.best_level:
        mt_session.best_level = mt_session.level

    db.add(mt_session)
    db.commit()
    db.refresh(attempt)

    # Parse solution steps for response
    solution_steps = []
    if solution_steps_json:
        solution_steps = json.loads(solution_steps_json)

    return {
        "correct": correct,
        "solution_steps": solution_steps,
        "staircase_result": staircase_result,
    }


@router.post("/sessions/{session_id}/consolidate")
def consolidate_session(session_id: int, db: Session = Depends(get_db)):
    """Close a math thinking session and create a PracticeSession for timeline tracking."""
    mt_session = db.get(MathThinkingSession, session_id)
    if not mt_session:
        raise HTTPException(404, "Math session not found")
    if not mt_session.is_active:
        raise HTTPException(400, "Session already consolidated")
    if mt_session.total_rounds < 3:
        raise HTTPException(400, "Minimum 3 problems required before consolidation")

    mt_session.is_active = False

    session_data = {
        "type": "math_thinking",
        "total_rounds": mt_session.total_rounds,
        "best_level": mt_session.best_level,
        "final_level": mt_session.level,
    }

    practice_session = PracticeSession(
        skill_id=mt_session.skill_id,
        what_i_practiced=f"Pensamiento Matemático — Nivel {mt_session.level}",
        micro_error_found=f"Math session: {mt_session.total_rounds} rounds, best level {mt_session.best_level}",
        difficulty=3,
        entry_mode="quick",
        duration_minutes=max(10, mt_session.total_rounds * 2),
        session_data=json.dumps(session_data),
    )
    db.add(practice_session)
    db.commit()
    db.refresh(practice_session)

    mt_session.consolidated_session_id = practice_session.id
    db.add(mt_session)
    db.commit()

    return {
        "status": "consolidated",
        "practice_session_id": practice_session.id,
        "rounds_completed": mt_session.total_rounds,
        "best_level": mt_session.best_level,
    }


@router.get("/sessions/{session_id}/state")
def get_session_state(session_id: int, db: Session = Depends(get_db)):
    """Get current math thinking session state."""
    mt_session = db.get(MathThinkingSession, session_id)
    if not mt_session:
        raise HTTPException(404, "Math session not found")

    return {
        "level": mt_session.level,
        "consecutive_correct": mt_session.consecutive_correct,
        "consecutive_incorrect": mt_session.consecutive_incorrect,
        "total_rounds": mt_session.total_rounds,
        "is_active": mt_session.is_active,
        "best_level": mt_session.best_level,
    }


@router.get("/sessions/{session_id}/history")
def get_round_history(session_id: int, db: Session = Depends(get_db)):
    """Get all rounds and attempts for a math thinking session."""
    mt_session = db.get(MathThinkingSession, session_id)
    if not mt_session:
        raise HTTPException(404, "Math session not found")

    rounds = db.exec(
        select(MathThinkingRound)
        .where(MathThinkingRound.session_id == session_id)
        .order_by(MathThinkingRound.created_at)
    ).all()

    result = []
    for r in rounds:
        attempts = db.exec(
            select(MathThinkingAttempt)
            .where(MathThinkingAttempt.round_id == r.id)
            .order_by(MathThinkingAttempt.created_at)
        ).all()

        result.append({
            "id": r.id,
            "level": r.level,
            "problem_text": r.problem_text,
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
