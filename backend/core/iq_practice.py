"""IQ Practice Engine — AI-generated puzzle generation, multiple-choice evaluation, staircase progression."""

import logging
from typing import Callable, Optional

from pydantic import BaseModel, Field

from core.puzzle_pools import get_pool_puzzle

logger = logging.getLogger(__name__)


class IQPuzzle(BaseModel):
    """Pydantic model for AI structured output of an IQ puzzle."""

    question: str = Field(..., description="El enunciado del puzzle en español")
    options: list[str] = Field(
        ..., description="Lista de 4 opciones de respuesta (A, B, C, D)"
    )
    correct_answer: str = Field(
        ..., description="El texto exacto de la opción correcta"
    )
    explanation: str = Field(
        ..., description="Explicación breve de por qué la opción correcta es la respuesta"
    )
    puzzle_type: str = Field(
        ..., description="Tipo: number_sequence, verbal_analogy, logical, o pattern"
    )
    source: Optional[str] = Field(
        default=None,
        description="Fuente verificada del dato o estudio (presente en pools estáticos)",
    )


PUZZLE_TYPE_LABELS = {
    "number_sequence": "Secuencia Numérica",
    "verbal_analogy": "Analogía Verbal",
    "logical": "Razonamiento Lógico",
    "pattern": "Reconocimiento de Patrones",
}

PUZZLE_TYPE_PROMPTS = {
    "number_sequence": (
        "Generá una secuencia numérica donde la persona debe encontrar "
        "el siguiente número. Incluí 4 opciones (A, B, C, D). "
        "La regla debe ser clara pero no trivial."
    ),
    "verbal_analogy": (
        "Generá una analogía verbal del tipo 'X es a Y como A es a ?'. "
        "Incluí 4 opciones (A, B, C, D). "
        "La relación debe ser semántica, no obvia."
    ),
    "logical": (
        "Generá un problema de razonamiento lógico (silogismos, "
        "deducción, ordenamiento, etc.). Incluí 4 opciones (A, B, C, D). "
        "Debe requerir pensamiento deductivo."
    ),
    "pattern": (
        "Generá un problema de reconocimiento de patrones abstractos "
        "descrito textualmente (series, matrices, transformaciones). "
        "Incluí 4 opciones (A, B, C, D). "
        "El patrón debe ser identificable pero no inmediato."
    ),
}


def generate_puzzle(
    level: int,
    config: dict,
    router_fn: Callable,
    session_id: Optional[int] = None,
    skill_id: Optional[int] = None,
    db=None,
) -> dict:
    """Generate an IQ puzzle using AI with structured output.

    For level 1 a curated, verified pool of 8 puzzles is used and rotated
    per session to avoid repetition (and to skip the ~5s AI round-trip).
    For level 2+ the AI path is used: a level-appropriate prompt is
    built from config, *router_fn* is called with the IQPuzzle Pydantic
    model, the response is validated (4 options, correct_answer in
    options), and up to 2 additional retries are attempted. Falls back
    to a simple puzzle when all retries fail.

    Args:
        level: Difficulty level (1–10).
        config: Full skill config dict (from iq-practice.yaml).
        router_fn: ``router.execute_with_router`` callable.
        session_id: Practice session ID used to track pool rotation.
            When ``None`` the pool is still used (with no rotation
            tracking) for level 1.

    Returns:
        dict with keys ``question``, ``options``, ``correct_answer``,
        ``explanation``, ``puzzle_type``, and ``source``.
    """
    # Fast path: level 1 uses the static pool to avoid the AI round-trip
    # and to guarantee variety without falling back to the same puzzle.
    pool_puzzle = get_pool_puzzle("iq_practice", level, session_id)
    if pool_puzzle is not None:
        return pool_puzzle

    levels = config.get("levels", {})
    level_config = levels.get(level, levels.get(1, {}))

    types: list[str] = level_config.get("types", ["number_sequence"])
    difficulty: str = level_config.get("difficulty", "easy")
    label: str = level_config.get("label", "básico")

    # Pick a random puzzle type from the available types for this level
    import random
    puzzle_type = random.choice(types)
    type_prompt = PUZZLE_TYPE_PROMPTS.get(
        puzzle_type, PUZZLE_TYPE_PROMPTS["number_sequence"]
    )
    type_label = PUZZLE_TYPE_LABELS.get(puzzle_type, puzzle_type)

    system_prompt = (
        f"Eres un generador de puzzles de inteligencia (IQ). Generá UN puzzle "
        f"de nivel {level} (nivel {label}, dificultad {difficulty}). "
        f"Tipo: {type_label}. "
        'Respondé ÚNICAMENTE en formato JSON válido con los campos: '
        '"question", "options" (lista de 4 strings), '
        '"correct_answer" (el texto exacto de la opción correcta), '
        '"explanation" (string), '
        '"puzzle_type" (string del tipo). '
        "NO incluyas texto fuera del JSON. NO uses markdown."
    )

    user_prompt = type_prompt + (
        f" Nivel {level} ({label}), dificultad {difficulty}. "
        "Asegurate de que exactamente UNA de las 4 opciones sea correcta "
        "y que las otras 3 sean plausibles pero incorrectas."
    )

    # Inject learning patterns if available (graceful degradation)
    if db and skill_id:
        try:
            from services.learning_patterns_service import format_patterns_for_prompt
            patterns_text = format_patterns_for_prompt(db, skill_id, "iq_practice")
            if patterns_text:
                user_prompt += f"\n\n{patterns_text}\n\nAdaptá el puzzle para reforzar las áreas donde el usuario tiene más errores."
        except Exception:
            pass  # Graceful degradation — generate normally if patterns fail

    last_error: Optional[str] = None

    for attempt in range(3):
        if attempt > 0:
            user_prompt = (
                f"Generá un puzzle de tipo {type_label}, nivel {level}, "
                f"dificultad {difficulty}. "
                "Debe tener EXACTAMENTE 4 opciones. "
                "correct_answer DEBE coincidir textualmente con una de las opciones."
            )
            if last_error:
                user_prompt += f"\n\n⚠ Error previo: {last_error}. Corregí."

        result = router_fn(
            task_type="iq_puzzle",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=IQPuzzle,
        )

        if result is None:
            last_error = "La IA no devolvió respuesta"
            logger.warning("generate_puzzle attempt %d/3: None", attempt + 1)
            continue

        if not result.options or len(result.options) != 4:
            last_error = f"Se requieren 4 opciones, se obtuvieron {len(result.options or [])}"
            logger.warning("generate_puzzle attempt %d/3: %s", attempt + 1, last_error)
            continue

        if result.correct_answer not in result.options:
            last_error = f"correct_answer no está en las opciones: {result.correct_answer!r}"
            logger.warning("generate_puzzle attempt %d/3: %s", attempt + 1, last_error)
            continue

        # Valid puzzle
        return {
            "question": result.question,
            "options": result.options,
            "correct_answer": result.correct_answer,
            "explanation": result.explanation,
            "puzzle_type": result.puzzle_type,
            "source": getattr(result, "source", None),
        }

    # All retries exhausted — fallback
    logger.error("generate_puzzle failed after 3 attempts — using fallback puzzle")
    return {
        "question": "¿Qué número sigue en la secuencia? 2, 4, 6, 8, ?",
        "options": ["9", "10", "11", "12"],
        "correct_answer": "10",
        "explanation": "La secuencia suma 2 cada vez: 2, 4, 6, 8, 10.",
        "puzzle_type": "number_sequence",
        "source": None,
    }


def evaluate_attempt(user_answer: str, correct_answer: str) -> bool:
    """Compare *user_answer* to *correct_answer* (exact match, trimmed)."""
    return user_answer.strip().lower() == correct_answer.strip().lower()


def calculate_staircase(
    level: int,
    was_correct: bool,
    consecutive_correct: int,
    consecutive_incorrect: int,
) -> dict:
    """Apply the staircase algorithm.

    This is a thin re-export of ``core.staircase.calculate_staircase`` to
    preserve the import path used by the IQ practice routes. See
    ``core/staircase.py`` for the full algorithm (redistribution model,
    5 to advance, 3 to retreat, UX protection when no correct yet).
    """
    from core.staircase import calculate_staircase as _impl
    return _impl(level, was_correct, consecutive_correct, consecutive_incorrect)
