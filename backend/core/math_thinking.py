"""Math Thinking Game Engine — AI problem generation, numeric evaluation, staircase progression."""

import logging
import math
from typing import Callable, Optional

from pydantic import BaseModel, Field

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


def generate_problem(
    level: int,
    config: dict,
    router_fn: Callable,
) -> dict:
    """Generate a math problem using AI with structured output.

    Builds a level-appropriate prompt from config, calls *router_fn* with
    the MathProblem Pydantic model, validates the returned answer (must be
    a finite float), and retries up to 2 additional times on invalid
    responses (NaN, None, infinity).  Falls back to a trivial problem when
    all retries are exhausted.

    Args:
        level: Difficulty level (1–10).
        config: Full skill config dict (from math-thinking.yaml).
        router_fn: ``router.execute_with_router`` callable.

    Returns:
        dict with keys ``question``, ``correct_answer``, ``solution_steps``.
    """
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
        }

    # All retries exhausted — fallback
    logger.error(
        "generate_problem failed after 3 attempts — using fallback problem"
    )
    return {
        "question": "¿Cuánto es 2 + 2?",
        "correct_answer": 4.0,
        "solution_steps": ["Sumá 2 + 2 = 4."],
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
    """Apply the level-only staircase algorithm.

    Rules
    -----
    - **3 consecutive correct** at the same level → level up (+1), both
      counters reset to 0.
    - **3 consecutive incorrect** at the same level → level down (-1), both
      counters reset to 0.
    - **Floor**: minimum level is 1 (stay at 1 if would go below).
    - **Ceiling**: maximum level is 10 (stay at 10 if would go above).
    - **Partial** streaks increment the appropriate counter without a level
      change.

    Args:
        level: Current level (1–10).
        was_correct: Whether the last attempt was correct.
        consecutive_correct: Current correct-streak counter.
        consecutive_incorrect: Current incorrect-streak counter.

    Returns:
        dict with ``new_level``, ``new_consecutive_correct``,
        ``new_consecutive_incorrect``, ``level_changed`` (bool), and
        ``message`` (Spanish string).
    """
    if was_correct:
        new_consecutive_correct = consecutive_correct + 1
        new_consecutive_incorrect = 0

        if new_consecutive_correct >= 3:
            new_level = level + 1
            new_consecutive_correct = 0
            new_consecutive_incorrect = 0

            if new_level > 10:
                return {
                    "new_level": 10,
                    "new_consecutive_correct": 0,
                    "new_consecutive_incorrect": 0,
                    "level_changed": False,
                    "message": "¡En el nivel máximo! "
                    "Probá con problemas más complejos.",
                }

            return {
                "new_level": new_level,
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
                "level_changed": True,
                "message": f"¡Pasaste al nivel {new_level}!",
            }

        # Partial correct
        return {
            "new_level": level,
            "new_consecutive_correct": new_consecutive_correct,
            "new_consecutive_incorrect": 0,
            "level_changed": False,
            "message": f"¡Correcto! ({new_consecutive_correct}/3 para subir)",
        }

    # --- Incorrect ---
    new_consecutive_correct = 0
    new_consecutive_incorrect = consecutive_incorrect + 1

    if new_consecutive_incorrect >= 3:
        new_level = level - 1
        new_consecutive_correct = 0
        new_consecutive_incorrect = 0

        if new_level < 1:
            return {
                "new_level": 1,
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
                "level_changed": False,
                "message": "En el nivel mínimo. Seguí practicando.",
            }

        return {
            "new_level": new_level,
            "new_consecutive_correct": 0,
            "new_consecutive_incorrect": 0,
            "level_changed": True,
            "message": f"Bajaste al nivel {new_level}. Seguí practicando.",
        }

    # Partial incorrect
    return {
        "new_level": level,
        "new_consecutive_correct": 0,
        "new_consecutive_incorrect": new_consecutive_incorrect,
        "level_changed": False,
        "message": f"Incorrecto. ({new_consecutive_incorrect}/3 errores)",
    }
