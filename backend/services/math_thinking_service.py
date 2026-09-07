import json
import os
from functools import lru_cache
from typing import Optional

import yaml
from pydantic import BaseModel
from sqlmodel import Session

from core import router as core_router
from core.math_thinking import calculate_staircase, evaluate_attempt, generate_problem
from models.models import MathThinkingAttempt, MathThinkingRound, MathThinkingSession
from services.game_base import consolidar_sesion_base, iniciar_sesion_base
from services.learning_patterns_service import record_error


class HintResponse(BaseModel):
    hint: str


@lru_cache(maxsize=1)
def load_skill_config():
    # Path: backend/services/ → backend/ → skills/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "skills", "math-thinking.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)

def iniciar_sesion(db: Session, skill_id: int) -> MathThinkingSession:
    return iniciar_sesion_base(db, MathThinkingSession, skill_id)

def crear_round(db: Session, session_id: int) -> tuple[MathThinkingRound, dict]:
    mt_session = db.get(MathThinkingSession, session_id)
    if not mt_session:
        raise ValueError("Math session not found")
    if not mt_session.is_active:
        raise ValueError("Math session is already closed")

    config = load_skill_config()
    problem = generate_problem(
        mt_session.level,
        config,
        core_router.execute_with_router,
        session_id=session_id,
        skill_id=mt_session.skill_id,
        db=db,
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

    return round_obj, problem

def enviar_intento(db: Session, round_id: int, user_answer: float) -> dict:
    round_obj = db.get(MathThinkingRound, round_id)
    if not round_obj:
        raise ValueError("Round not found")

    mt_session = db.get(MathThinkingSession, round_obj.session_id)
    if not mt_session:
        raise ValueError("Session not found")

    correct = evaluate_attempt(user_answer, round_obj.correct_answer)

    staircase_result = calculate_staircase(
        mt_session.level,
        correct,
        mt_session.consecutive_correct,
        mt_session.consecutive_incorrect,
    )

    # Always return pre-generated solution steps (collapsed in UI by default)
    solution_steps_json = round_obj.solution_steps_json

    attempt = MathThinkingAttempt(
        round_id=round_id,
        user_answer=user_answer,
        correct=correct,
        solution_steps_json=solution_steps_json,
    )
    db.add(attempt)
    db.flush()  # get attempt.id for learning patterns

    # Record error pattern for adaptive AI (no-op if correct)
    if not correct:
        record_error(
            db,
            skill_id=mt_session.skill_id,
            skill_type="problem_set",
            session_id=mt_session.id,
            round_id=round_id,
            attempt_id=attempt.id,
            is_correct=correct,
            user_answer=user_answer,
            correct_answer=round_obj.correct_answer,
            level=mt_session.level,
        )

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

def get_hint(db: Session, round_id: int) -> dict:
    """Generate an AI hint for the current math problem without revealing the answer."""
    round_obj = db.get(MathThinkingRound, round_id)
    if not round_obj:
        raise ValueError("Round not found")

    hint_system = (
        "Sos un tutor de matemáticas. Generá UNA pista breve y útil para el problema. "
        "NO reveles la respuesta final. Solo orientá con un paso o estrategia. "
        "Máximo 2 oraciones."
    )
    hint_user = (
        f"Problema: {round_obj.problem_text}\n"
        f"Nivel: {round_obj.level}\n"
        "Dame una pista sin revelar la respuesta."
    )

    try:
        result = core_router.execute_with_router(
            task_type="math_hint",
            system_prompt=hint_system,
            user_prompt=hint_user,
            response_model=HintResponse,
        )
        hint_text = result.hint if result else "Pensá: ¿qué operación te acerca más a la respuesta? Probá descomponer el problema."
    except Exception:
        hint_text = "Pensá: ¿qué operación te acerca más a la respuesta? Probá descomponer el problema."

    return {"hint": hint_text}

def consolidar_sesion(db: Session, session_id: int, elapsed_seconds: Optional[int]) -> dict:
    def build_session_data(gs):
        data = {
            "type": "math_thinking",
            "total_rounds": gs.total_rounds,
            "best_level": gs.best_level,
            "final_level": gs.level,
        }
        if elapsed_seconds is not None:
            data["elapsed_seconds"] = elapsed_seconds
        return data

    def build_practice_fields(gs):
        return {
            "skill_id": gs.skill_id,
            "what_i_practiced": f"Pensamiento Matemático — Nivel {gs.level}",
            "micro_error_found": f"Math session: {gs.total_rounds} rounds, best level {gs.best_level}",
            "difficulty": 3,
            "entry_mode": "quick",
            "duration_minutes": max(10, gs.total_rounds * 2),
        }

    practice_session, gs = consolidar_sesion_base(
        db, MathThinkingSession, session_id, elapsed_seconds,
        "Math", build_session_data, build_practice_fields,
        min_rounds_message="Minimum 3 problems required before consolidation",
    )

    return {
        "status": "consolidated",
        "practice_session_id": practice_session.id,
        "rounds_completed": gs.total_rounds,
        "best_level": gs.best_level,
        "summary": {
            "rounds_completed": gs.total_rounds,
            "best_level": gs.best_level,
        },
    }
