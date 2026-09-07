"""Shared staircase (level progression) logic for math_thinking and iq_practice.

The staircase uses a redistribution model rather than a strict consecutive
streak model. Two counters — ``consecutive_correct`` (cc) and
``consecutive_incorrect`` (ci) — are maintained independently.

Rules
-----
- **On correct**: ``cc += 1``. If ``cc >= 5``, level up and reset both
  counters to 0. The ``ci`` counter is NOT reset on correct — failures
  accumulate over time and only clear on level change.
- **On incorrect** (when ``cc > 0``): the failure is *redistributed* —
  one unit moves from ``cc`` to ``ci`` (``cc -= 1``, ``ci += 1``). If
  ``ci >= 3``, level down and reset both counters to 0. This means a
  single mistake costs a correct, but the system tracks the total
  failure budget separately.
- **On incorrect** (when ``cc == 0``): the failure is *absorbed*. No
  counter changes. This is the UX-protection mechanic: a user who
  starts a fresh session and fails the first attempt doesn't get
  immediately punished ("para que colocar como falla"). The user can
  experiment at the bottom of a level without accumulating a
  frustrating failure counter.

Thresholds are uniform (5 to advance, 3 to retreat) for all levels.
The previous "5/3 adaptive for levels 1-2, 3/3 for levels 3-10" was
removed because the user reported it was a frustrating streak model
("5 seguids para pasar, 3 seguidas para bajar") that didn't match how
deliberate practice feels.

This module is imported by ``core.math_thinking`` and ``core.iq_practice``
to keep the algorithm in a single place.
"""

from typing import TypedDict


class StaircaseResult(TypedDict):
    """Result of a single staircase step."""

    new_level: int
    new_consecutive_correct: int
    new_consecutive_incorrect: int
    level_changed: bool
    message: str


# Thresholds (uniform across all levels).
CORRECT_THRESHOLD = 5
INCORRECT_THRESHOLD = 3


def calculate_staircase(
    level: int,
    was_correct: bool,
    consecutive_correct: int,
    consecutive_incorrect: int,
) -> StaircaseResult:
    """Apply the redistribution-based staircase algorithm.

    See module docstring for full rules. Both math_thinking and
    iq_practice call this function and return the result to the API
    layer, which persists the new counters on the session row.
    """
    if was_correct:
        new_cc = consecutive_correct + 1
        # Dynamic forgiveness: if there are failures, reduce the failure
        # count on a correct attempt.
        new_ci = max(0, consecutive_incorrect - 1)

        if new_cc >= CORRECT_THRESHOLD:
            new_level = level + 1
            if new_level > 10:
                return {
                    "new_level": 10,
                    "new_consecutive_correct": 0,
                    "new_consecutive_incorrect": 0,
                    "level_changed": False,
                    "message": (
                        "¡En el nivel máximo! "
                        "Probá con problemas más complejos."
                    ),
                }
            return {
                "new_level": new_level,
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
                "level_changed": True,
                "message": f"¡Pasaste al nivel {new_level}!",
            }

        return {
            "new_level": level,
            "new_consecutive_correct": new_cc,
            "new_consecutive_incorrect": new_ci,
            "level_changed": False,
            "message": (
                f"¡Correcto! ({new_cc}/{CORRECT_THRESHOLD} para subir)"
            ),
        }

    # --- Incorrect ---
    if consecutive_correct == 0:
        # UX protection: no correct buffer to redistribute, the
        # failure is absorbed. The user can experiment at the start
        # of a level without accumulating a frustrating failure
        # counter ("para que colocar como falla").
        return {
            "new_level": level,
            "new_consecutive_correct": 0,
            "new_consecutive_incorrect": consecutive_incorrect,
            "level_changed": False,
            "message": "Incorrecto. Seguí intentando.",
        }

    # Redistribute: one unit moves from cc to ci.
    new_cc = consecutive_correct - 1
    new_ci = consecutive_incorrect + 1

    if new_ci >= INCORRECT_THRESHOLD:
        new_level = level - 1
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

    return {
        "new_level": level,
        "new_consecutive_correct": new_cc,
        "new_consecutive_incorrect": new_ci,
        "level_changed": False,
        "message": (
            f"Incorrecto. ({new_ci}/{INCORRECT_THRESHOLD} errores, "
            f"-1 correcta)"
        ),
    }
