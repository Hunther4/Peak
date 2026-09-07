"""Math Thinking Game Engine — AI problem generation, numeric evaluation, staircase progression."""

import logging
import math
from typing import Callable, Optional

from pydantic import BaseModel, Field

from core.puzzle_pools import get_pool_puzzle

logger = logging.getLogger(__name__)


class MathProblem(BaseModel):
    """Pydantic model for AI structured output of a math problem."""

    question: str = Field(..., description="El problema matemático en español")
    correct_answer: float = Field(
        ..., description="La respuesta correcta como número finito"
    )
    solution_steps: list[str] = Field(
        ..., description="Pasos detallados para resolver el problema"
    )
    source: Optional[str] = Field(
        default=None,
        description="Fuente verificada del dato (presente en pools estáticos)",
    )


def generate_problem(
    level: int,
    config: dict,
    router_fn: Callable,
    session_id: Optional[int] = None,
    skill_id: Optional[int] = None,
    db=None,
) -> dict:
    """Generate a math problem using AI with structured output.

    For level 1 a curated, verified pool of 8 problems (real-world data
    from citable sources) is used and rotated per session to avoid
    repetition. For level 2+ the AI path is used: a level-appropriate
    prompt is built from config, *router_fn* is called with the
    MathProblem Pydantic model, the answer is validated (must be a finite
    float), and up to 2 additional retries are attempted on invalid
    responses (NaN, None, infinity). Falls back to a trivial problem
    when all retries are exhausted.

    Args:
        level: Difficulty level (1–10).
        config: Full skill config dict (from math-thinking.yaml).
        router_fn: ``router.execute_with_router`` callable.
        session_id: Math session ID used to track pool rotation. When
            ``None`` the pool is still used (with no rotation tracking)
            for level 1.

    Returns:
        dict with keys ``question``, ``correct_answer``,
        ``solution_steps``, ``source``.
    """
    # Fast path: levels 1-2 use the static pool to avoid the AI round-trip
    # and to guarantee variety without falling back to the same problem.
    # Level 1 is ALWAYS static — no AI call ever.
    pool_problem = get_pool_puzzle("problem_set", level, session_id)
    if pool_problem is not None:
        return pool_problem

    # Level 1 should never reach here (pool always has problems).
    # If it does, return a hardcoded fallback — level 1 MUST be static.
    if level <= 1:
        logger.warning(
            "generate_problem: pool returned None for level %d — using hardcoded fallback", level
        )
        import random
        _L1_FALLBACKS = [
            {"q": "¿Cuánto es 15 + 27?", "a": 42.0, "s": ["15 + 27 = 42"]},
            {"q": "¿Cuánto es 100 - 38?", "a": 62.0, "s": ["100 - 38 = 62"]},
            {"q": "¿Cuánto es 6 × 7?", "a": 42.0, "s": ["6 × 7 = 42"]},
            {"q": "¿Cuánto es 56 ÷ 8?", "a": 7.0, "s": ["56 ÷ 8 = 7"]},
            {"q": "¿Cuánto es 9 × 9?", "a": 81.0, "s": ["9 × 9 = 81"]},
        ]
        fb = random.choice(_L1_FALLBACKS)
        return {"question": fb["q"], "correct_answer": fb["a"], "solution_steps": fb["s"], "source": "fallback_level1"}

    difficulties = config.get("difficulties", {})
    level_config = difficulties.get(level, difficulties.get(1, {}))

    topics: list[str] = level_config.get("topics", ["suma", "resta"])
    problem_types: list[str] = level_config.get(
        "problem_types", ["cálculo directo"]
    )
    label: str = level_config.get("label", "básico")

    topic_str = ", ".join(topics) if topics else "suma y resta"
    problem_type_str = (
        ", ".join(problem_types) if problem_types else "cálculo directo"
    )

    system_prompt = (
        f"Eres un generador de problemas matemáticos. Generá UN problema "
        f"de nivel {level} (nivel {label}). "
        'Respondé ÚNICAMENTE en formato JSON válido con los campos: '
        '"question", "correct_answer" (número), '
        '"solution_steps" (lista de strings). '
        "NO incluyas texto fuera del JSON. NO uses markdown."
    )

    user_prompt = (
        f"Generá un problema de {topic_str} del tipo {problem_type_str}. "
        "Incluí la respuesta correcta como número y los pasos de solución."
    )

    # Inject learning patterns if available (graceful degradation)
    if db and skill_id:
        try:
            from services.learning_patterns_service import format_patterns_for_prompt
            patterns_text = format_patterns_for_prompt(db, skill_id, "problem_set")
            if patterns_text:
                user_prompt += f"\n\n{patterns_text}\n\nAdaptá el problema para reforzar las áreas donde el usuario tiene más errores."
        except Exception:
            pass  # Graceful degradation — generate normally if patterns fail

    last_error: Optional[str] = None

    for attempt in range(3):  # initial + 2 retries
        if attempt > 0:
            # Stricter instruction on retry
            user_prompt = (
                f"Generá un problema de {topic_str} del tipo "
                f"{problem_type_str}. "
                "La respuesta correcta DEBE ser un número finito válido "
                "(no NaN, no infinito). "
                "Incluí los pasos de solución detallados."
            )
            if last_error:
                user_prompt += (
                    f"\n\n⚠ Error previo: {last_error}. Corregí el formato."
                )

        result = router_fn(
            task_type="math_problem",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=MathProblem,
        )

        if result is None:
            last_error = "La IA no devolvió una respuesta válida"
            logger.warning(
                "generate_problem attempt %d/3: AI returned None",
                attempt + 1,
            )
            continue

        answer = result.correct_answer

        if (
            answer is None
            or not isinstance(answer, (int, float))
            or math.isnan(answer)
            or math.isinf(answer)
        ):
            last_error = f"correct_answer inválido: {answer!r}"
            logger.warning(
                "generate_problem attempt %d/3: %s",
                attempt + 1,
                last_error,
            )
            continue

        # Valid answer → return immediately
        return {
            "question": result.question,
            "correct_answer": float(answer),
            "solution_steps": result.solution_steps,
            "source": getattr(result, "source", None),
        }

    # All retries exhausted — fallback
    logger.error(
        "generate_problem failed after 3 attempts — using fallback problem"
    )
    return {
        "question": "¿Cuánto es 2 + 2?",
        "correct_answer": 4.0,
        "solution_steps": ["Sumá 2 + 2 = 4."],
        "source": None,
    }


def evaluate_attempt(user_answer: float, correct_answer: float) -> bool:
    """Compare *user_answer* to *correct_answer* with a tolerance of 0.01.

    Args:
        user_answer: The answer submitted by the user.
        correct_answer: The canonical correct answer.

    Returns:
        ``True`` when ``abs(user_answer - correct_answer) < 0.01``.
    """
    return abs(user_answer - correct_answer) < 0.01


def calculate_staircase(
    level: int,
    was_correct: bool,
    consecutive_correct: int,
    consecutive_incorrect: int,
) -> dict:
    """Apply the staircase algorithm.

    This is a thin re-export of ``core.staircase.calculate_staircase`` to
    preserve the import path used by the math thinking routes. See
    ``core/staircase.py`` for the full algorithm (redistribution model,
    5 to advance, 3 to retreat, UX protection when no correct yet).
    """
    from core.staircase import calculate_staircase as _impl
    return _impl(level, was_correct, consecutive_correct, consecutive_incorrect)
