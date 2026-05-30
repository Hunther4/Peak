"""IQ Practice Engine — AI-generated puzzle generation, multiple-choice evaluation, staircase progression."""

import logging
from typing import Callable, Optional
from pydantic import BaseModel, Field

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
) -> dict:
    """Generate an IQ puzzle using AI with structured output.

    Builds a level-appropriate prompt from config, calls *router_fn* with
    the IQPuzzle Pydantic model, validates the response has 4 options with
    one matching correct_answer, and retries up to 2 additional times on
    invalid responses. Falls back to a simple puzzle when all retries fail.

    Args:
        level: Difficulty level (1–10).
        config: Full skill config dict (from iq-practice.yaml).
        router_fn: ``router.execute_with_router`` callable.

    Returns:
        dict with keys ``question``, ``options``, ``correct_answer``,
        ``explanation``, ``puzzle_type``.
    """
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
        }

    # All retries exhausted — fallback
    logger.error("generate_puzzle failed after 3 attempts — using fallback puzzle")
    return {
        "question": "¿Qué número sigue en la secuencia? 2, 4, 6, 8, ?",
        "options": ["9", "10", "11", "12"],
        "correct_answer": "10",
        "explanation": "La secuencia suma 2 cada vez: 2, 4, 6, 8, 10.",
        "puzzle_type": "number_sequence",
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
    """Apply the level-only staircase algorithm (same as math_thinking).

    Rules
    -----
    - **3 consecutive correct** at the same level → level up (+1), counters reset.
    - **3 consecutive incorrect** at the same level → level down (-1), counters reset.
    - **Floor**: minimum level is 1.
    - **Ceiling**: maximum level is 10.

    Returns:
        dict with ``new_level``, ``new_consecutive_correct``,
        ``new_consecutive_incorrect``, ``level_changed``, ``message``.
    """
    if was_correct:
        new_cc = consecutive_correct + 1
        new_ci = 0

        if new_cc >= 3:
            new_lvl = level + 1
            if new_lvl > 10:
                return {
                    "new_level": 10,
                    "new_consecutive_correct": 0,
                    "new_consecutive_incorrect": 0,
                    "level_changed": False,
                    "message": "¡Nivel máximo alcanzado! Probá con puzzles más complejos.",
                }
            return {
                "new_level": new_lvl,
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
                "level_changed": True,
                "message": f"¡Subiste al nivel {new_lvl}!",
            }

        return {
            "new_level": level,
            "new_consecutive_correct": new_cc,
            "new_consecutive_incorrect": 0,
            "level_changed": False,
            "message": f"¡Correcto! ({new_cc}/3 para subir)",
        }

    # Incorrect
    new_cc = 0
    new_ci = consecutive_incorrect + 1

    if new_ci >= 3:
        new_lvl = max(1, level - 1)
        if new_lvl == level:
            return {
                "new_level": 1,
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
                "level_changed": False,
                "message": "Nivel mínimo. Seguí practicando.",
            }
        return {
            "new_level": new_lvl,
            "new_consecutive_correct": 0,
            "new_consecutive_incorrect": 0,
            "level_changed": True,
            "message": f"Bajaste al nivel {new_lvl}. Seguí practicando.",
        }

    return {
        "new_level": level,
        "new_consecutive_correct": 0,
        "new_consecutive_incorrect": new_ci,
        "level_changed": False,
        "message": f"Incorrecto. ({new_ci}/3 errores)",
    }
