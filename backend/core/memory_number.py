"""Memory Number Game Engine — staircase difficulty, number generation, phase logic."""

import json
import random
from typing import Optional

# Phase configuration
PHASES = [
    {"phase": 1, "min_span": 4, "max_span": 7, "digit_max": 1, "timing": 5},
    {"phase": 2, "min_span": 8, "max_span": 12, "digit_max": 1, "timing": 5},
    {"phase": 3, "min_span": 13, "max_span": 18, "digit_max": 2, "timing": 4},
    {"phase": 4, "min_span": 19, "max_span": 25, "digit_max": 2, "timing": 4},
    {"phase": 5, "min_span": 26, "max_span": 30, "digit_max": 3, "timing": 4},
    {"phase": 6, "min_span": 31, "max_span": 40, "digit_max": 4, "timing": 3},
    {"phase": 7, "min_span": 50, "max_span": 80, "digit_max": 9, "timing": 3, "ai_assisted": True},
]


def get_phase_config(phase: int) -> dict:
    """Get configuration for a given phase number (1-7)."""
    for p in PHASES:
        if p["phase"] == phase:
            return p
    return PHASES[0]


def generate_numbers(span: int, digit_max: int, ai_assisted: bool = False) -> list:
    """Generate a list of random numbers.
    
    - If digit_max == 1: single digits (0-9)
    - If digit_max > 1: numbers from 0 to (10^digit_max - 1)
    - If ai_assisted: use wider range for phase 7
    """
    if ai_assisted:
        # Phase 7: mix of 1-4 digit numbers for variety
        return [random.randint(0, 10 ** random.randint(1, 4) - 1) for _ in range(span)]
    
    max_val = 10 ** digit_max - 1
    return [random.randint(0, max_val) for _ in range(span)]


def calculate_staircase(
    current_span: int,
    phase: int,
    was_correct: bool,
    consecutive_correct: int,
    consecutive_incorrect: int,
) -> dict:
    """Apply the staircase algorithm.
    
    Rules:
    - 3 consecutive correct at same span → span += 1
    - 1 error → reset consecutive_correct, increment consecutive_incorrect
    - 3 consecutive incorrect at same span → span -= 2
    - Span cannot go below min_span of current phase
    - Span cannot go above max_span of current phase
    
    Returns dict with: new_span, new_consecutive_correct, new_consecutive_incorrect, 
                       phase_changed, new_phase, message
    """
    phase_config = get_phase_config(phase)
    
    if was_correct:
        new_consecutive_correct = consecutive_correct + 1
        new_consecutive_incorrect = 0
        
        if new_consecutive_correct >= 3:
            new_span = current_span + 1
            new_consecutive_correct = 0
            
            # Check if should advance to next phase
            if new_span > phase_config["max_span"]:
                if phase < 7:
                    new_phase = phase + 1
                    new_phase_config = get_phase_config(new_phase)
                    new_span = new_phase_config["min_span"]
                    return {
                        "new_span": new_span,
                        "new_consecutive_correct": 0,
                        "new_consecutive_incorrect": 0,
                        "phase_changed": True,
                        "new_phase": new_phase,
                        "message": f"¡Avanzaste a fase {new_phase}!",
                    }
                else:
                    new_span = phase_config["max_span"]
                    return {
                        "new_span": new_span,
                        "new_consecutive_correct": 0,
                        "new_consecutive_incorrect": 0,
                        "phase_changed": False,
                        "new_phase": phase,
                        "message": "¡En el techo! Prueba con más dígitos o tiempo reducido.",
                    }
            
            return {
                "new_span": new_span,
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
                "phase_changed": False,
                "new_phase": phase,
                "message": f"¡3 aciertos seguidos! Span sube a {new_span}",
            }
        
        return {
            "new_span": current_span,
            "new_consecutive_correct": new_consecutive_correct,
            "new_consecutive_incorrect": 0,
            "phase_changed": False,
            "new_phase": phase,
            "message": "Correcto!",
        }
    else:
        new_consecutive_correct = 0
        new_consecutive_incorrect = consecutive_incorrect + 1
        
        if new_consecutive_incorrect >= 3:
            new_span = current_span - 2
            if new_span < phase_config["min_span"]:
                # Check if should regress to previous phase
                if phase > 1:
                    new_phase = phase - 1
                    new_phase_config = get_phase_config(new_phase)
                    new_span = new_phase_config["max_span"]
                    return {
                        "new_span": new_span,
                        "new_consecutive_correct": 0,
                        "new_consecutive_incorrect": 0,
                        "phase_changed": True,
                        "new_phase": new_phase,
                        "message": f"3 errores seguidos — retrocedes a fase {new_phase}",
                    }
                else:
                    new_span = phase_config["min_span"]
            
            return {
                "new_span": new_span,
                "new_consecutive_correct": 0,
                "new_consecutive_incorrect": 0,
                "phase_changed": False,
                "new_phase": phase,
                "message": f"3 errores — span baja a {new_span}",
            }
        
        return {
            "new_span": current_span,
            "new_consecutive_correct": 0,
            "new_consecutive_incorrect": new_consecutive_incorrect,
            "phase_changed": False,
            "new_phase": phase,
            "message": "Incorrecto. Intentá de nuevo.",
        }


def evaluate_attempt(expected_numbers: list, submitted_numbers: list) -> dict:
    """Compare expected vs submitted numbers position by position.
    
    Returns dict with: correct (bool), correct_positions (int), total_positions (int), errors (list)
    """
    total = len(expected_numbers)
    
    # HIGH Fix: Extra/missing submitted numbers mark attempt as incorrect
    if len(submitted_numbers) != total:
        return {
            "correct": False,
            "correct_positions": 0,
            "total_positions": total,
            "errors": [{"position": -1, "expected": total, "got": len(submitted_numbers)}],
        }

    errors = []
    correct_positions = 0
    
    for i in range(total):
        if submitted_numbers[i] != expected_numbers[i]:
            errors.append({"position": i, "expected": expected_numbers[i], "got": submitted_numbers[i]})
        else:
            correct_positions += 1
    
    return {
        "correct": correct_positions == total,
        "correct_positions": correct_positions,
        "total_positions": total,
        "errors": errors,
    }
