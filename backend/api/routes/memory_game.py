from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session, select
from datetime import datetime, timezone
import json
from typing import List
from pydantic import BaseModel

from core.database import engine
from core.memory_number import (
    generate_numbers, evaluate_attempt, calculate_staircase,
    get_phase_config,
)
from models.models import MemoryNumberSession, MemoryNumberRound, MemoryNumberAttempt
from models.models import Session as PracticeSession

router = APIRouter()


class GameSessionCreate(BaseModel):
    skill_id: int

class AttemptSubmission(BaseModel):
    submitted_numbers: List[int]

def get_db():
    with Session(engine) as session:
        yield session


@router.post("/sessions")
def create_game_session(body: GameSessionCreate, db: Session = Depends(get_db)):
    """Start a new memory game session."""
    session = MemoryNumberSession(skill_id=body.skill_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "id": session.id,
        "phase": session.phase,
        "current_span": session.current_span,
        "best_span": session.best_span,
        "best_phase": session.best_phase,
        "timing": get_phase_config(session.phase)["timing"],
    }


@router.post("/sessions/{session_id}/rounds")
def create_round(session_id: int, db: Session = Depends(get_db)):
    """Generate a new round of numbers based on current game session state."""
    game_session = db.get(MemoryNumberSession, session_id)
    if not game_session:
        raise HTTPException(404, "Game session not found")
    if not game_session.is_active:
        raise HTTPException(400, "Game session is already closed")
    
    phase_config = get_phase_config(game_session.phase)
    numbers = generate_numbers(
        game_session.current_span,
        phase_config["digit_max"],
        phase_config.get("ai_assisted", False),
    )
    
    round_obj = MemoryNumberRound(
        game_session_id=session_id,
        phase=game_session.phase,
        span=game_session.current_span,
        digit_max=phase_config["digit_max"],
        numbers_json=json.dumps(numbers),
        sequence_length=len(numbers),
        ai_assisted=phase_config.get("ai_assisted", False),
    )
    db.add(round_obj)
    
    # Track total rounds on the game session
    game_session.total_rounds += 1
    db.add(game_session)
    
    db.commit()
    db.refresh(round_obj)
    
    return {
        "id": round_obj.id,
        "phase": round_obj.phase,
        "span": round_obj.span,
        "length": round_obj.sequence_length,
        "timing": phase_config["timing"],
        # Numbers are sent to frontend — they'll be displayed one at a time
        "numbers": numbers,
    }


@router.post("/rounds/{round_id}/attempts")
def submit_attempt(
    round_id: int,
    body: AttemptSubmission,
    db: Session = Depends(get_db),
):
    """Submit a recall attempt and get position-by-position feedback."""
    round_obj = db.get(MemoryNumberRound, round_id)
    if not round_obj:
        raise HTTPException(404, "Round not found")
    
    expected = json.loads(round_obj.numbers_json)
    evaluation = evaluate_attempt(expected, body.submitted_numbers)
    
    attempt = MemoryNumberAttempt(
        round_id=round_id,
        submitted_numbers_json=json.dumps(body.submitted_numbers),
        correct=evaluation["correct"],
        correct_positions=evaluation["correct_positions"],
        total_positions=evaluation["total_positions"],
        errors_json=json.dumps(evaluation["errors"]) if evaluation["errors"] else None,
    )
    db.add(attempt)
    
    # Update staircase
    game_session = db.get(MemoryNumberSession, round_obj.game_session_id)
    
    # CRITICAL: result must be defined before if block to avoid crash if session missing
    result = {
        "new_span": round_obj.span,
        "new_phase": round_obj.phase,
        "phase_changed": False,
        "message": "",
        "new_consecutive_correct": 0,
        "new_consecutive_incorrect": 0
    }
    
    if game_session:
        result = calculate_staircase(
            game_session.current_span,
            game_session.phase,
            evaluation["correct"],
            game_session.consecutive_correct,
            game_session.consecutive_incorrect,
        )
        game_session.current_span = result["new_span"]
        game_session.consecutive_correct = result["new_consecutive_correct"]
        game_session.consecutive_incorrect = result["new_consecutive_incorrect"]
        
        if result["phase_changed"]:
            game_session.phase = result["new_phase"]
        
        # Track best: Use the updated session state
        if game_session.current_span > game_session.best_span:
            game_session.best_span = game_session.current_span
        if game_session.phase > game_session.best_phase:
            game_session.best_phase = game_session.phase
        
        db.add(game_session)
    
    db.commit()
    db.refresh(attempt)
    
    return {
        "id": attempt.id,
        "correct": evaluation["correct"],
        "correct_positions": evaluation["correct_positions"],
        "total_positions": evaluation["total_positions"],
        "errors": evaluation["errors"],
        "staircase_result": result,
        "next_timing": get_phase_config(result.get("new_phase", round_obj.phase))["timing"],
    }


@router.post("/sessions/{session_id}/consolidate")
def consolidate_session(session_id: int, db: Session = Depends(get_db)):
    """Close a game session and create a PracticeSession for timeline/streak tracking."""
    game_session = db.get(MemoryNumberSession, session_id)
    if not game_session:
        raise HTTPException(404, "Game session not found")
    if not game_session.is_active:
        raise HTTPException(400, "Session already consolidated")
    if game_session.total_rounds < 3:
        raise HTTPException(400, "Minimum 3 rounds required before consolidation")
    
    game_session.is_active = False
    
    # Create practice session
    session_data = {
        "type": "memory_number",
        "total_rounds": game_session.total_rounds,
        "best_span": game_session.best_span,
        "best_phase": game_session.best_phase,
        "final_phase": game_session.phase,
        "final_span": game_session.current_span,
    }
    
    practice_session = PracticeSession(
        skill_id=game_session.skill_id,
        what_i_practiced=f"Memorizar Números — Fase {game_session.phase}, Span {game_session.current_span}",
        micro_error_found=f"Game session: {game_session.total_rounds} rounds, best span {game_session.best_span}",
        difficulty=3,
        entry_mode="quick",
        duration_minutes=max(10, game_session.total_rounds * 2),
        session_data=json.dumps(session_data),
    )
    db.add(practice_session)
    db.commit()
    db.refresh(practice_session)
    
    game_session.consolidated_session_id = practice_session.id
    db.add(game_session)
    db.commit()
    
    return {
        "status": "consolidated",
        "practice_session_id": practice_session.id,
        "rounds_completed": game_session.total_rounds,
        "best_span": game_session.best_span,
        "best_phase": game_session.best_phase,
    }


@router.get("/sessions/{session_id}/state")
def get_game_state(session_id: int, db: Session = Depends(get_db)):
    """Get current game session state."""
    game_session = db.get(MemoryNumberSession, session_id)
    if not game_session:
        raise HTTPException(404, "Game session not found")
    
    return {
        "phase": game_session.phase,
        "current_span": game_session.current_span,
        "consecutive_correct": game_session.consecutive_correct,
        "consecutive_incorrect": game_session.consecutive_incorrect,
        "best_span": game_session.best_span,
        "best_phase": game_session.best_phase,
        "total_rounds": game_session.total_rounds,
        "is_active": game_session.is_active,
        "timing": get_phase_config(game_session.phase)["timing"],
    }


@router.get("/sessions/{session_id}/history")
def get_round_history(session_id: int, db: Session = Depends(get_db)):
    """Get all rounds and attempts for a game session."""
    game_session = db.get(MemoryNumberSession, session_id)
    if not game_session:
        raise HTTPException(404, "Game session not found")
    
    rounds = db.exec(
        select(MemoryNumberRound)
        .where(MemoryNumberRound.game_session_id == session_id)
        .order_by(MemoryNumberRound.created_at)
    ).all()
    
    result = []
    for r in rounds:
        attempts = db.exec(
            select(MemoryNumberAttempt)
            .where(MemoryNumberAttempt.round_id == r.id)
            .order_by(MemoryNumberAttempt.created_at)
        ).all()
        
        result.append({
            "id": r.id,
            "phase": r.phase,
            "span": r.span,
            "correct": any(a.correct for a in attempts) if attempts else None,
            "attempts": [
                {
                    "correct": a.correct,
                    "correct_positions": a.correct_positions,
                    "total_positions": a.total_positions,
                }
                for a in attempts
            ],
        })
    
    return {"rounds": result, "total": len(result)}
