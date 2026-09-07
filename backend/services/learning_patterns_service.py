"""Learning Patterns Service — error extraction, aggregation, sliding window.

Called after each attempt to:
1. Classify the error type
2. Store a LearningPattern row (raw metadata)
3. Upsert the ErrorPattern aggregation (count + severity)
4. Link the session via SessionError

Sliding window query returns last 25 patterns per skill for AI prompt injection.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session as DBSession
from sqlmodel import func, select

from models.models import (
    ErrorPattern,
    LearningPattern,
    SessionError,
)

# Error classification per skill type
# Maps (skill_type, is_correct, context) -> error_type
ERROR_TYPES = {
    "problem_set": {
        "arithmetic": "Error de cálculo básico",
        "conceptual": "Confusión de concepto matemático",
        "careless": "Error por descuido (sabía la respuesta)",
        "timeout": "Tiempo agotado sin respuesta",
    },
    "iq_practice": {
        "pattern_mismatch": "No identificó el patrón",
        "wrong_option": "Identificó patrón pero eligió opción incorrecta",
        "timeout": "Tiempo agotado sin respuesta",
        "careless": "Error por descuido",
    },
    "memory_number": {
        "position_error": "Recordó números pero en posición incorrecta",
        "sequence_error": "No recordó la secuencia completa",
        "timeout": "Tiempo agotado",
        "careless": "Error por descuido (secuencia corta)",
    },
}


def classify_error(
    skill_type: str,
    is_correct: bool,
    user_answer=None,
    correct_answer=None,
    puzzle_type: Optional[str] = None,
    response_time_ms: Optional[int] = None,
) -> Optional[str]:
    """Classify the error type for an incorrect attempt. Returns None if correct."""
    if is_correct:
        return None

    # Timeout detection (if response time > 30s)
    if response_time_ms and response_time_ms > 30000:
        return "timeout"

    if skill_type == "problem_set":
        # Arithmetic vs conceptual vs careless
        if user_answer is not None and correct_answer is not None:
            try:
                c_val = float(correct_answer)
                u_val = float(user_answer)
                diff = abs(u_val - c_val)
                denom = abs(c_val) if c_val != 0 else 1.0
                rel_diff = diff / denom
                if rel_diff <= 0.10:  # within 10% → careless (slight miscalculation)
                    return "careless"
                elif rel_diff >= 1.0 or (c_val * u_val < 0 and c_val != 0):  # off by 100%+ or opposite sign → conceptual
                    return "conceptual"
                return "arithmetic"
            except (ValueError, TypeError):
                return "conceptual"
        return "arithmetic"

    elif skill_type == "iq_practice":
        # IQ: if the answer doesn't match any pattern → pattern_mismatch
        if puzzle_type and user_answer and correct_answer:
            puzzle_types_map = {
                "number_sequence": ["A", "B", "C", "D"],
                "verbal_analogy": ["A", "B", "C", "D"],
                "logical": ["A", "B", "C", "D"],
                "pattern": ["A", "B", "C", "D"],
                "matrix": ["A", "B", "C", "D", "E", "F", "G", "H"],
                "classification": ["same", "different"],
                "analogy": ["A", "B", "C", "D", "E"],
                "series": ["A", "B", "C", "D", "E"],
            }
            expected_options = puzzle_types_map.get(puzzle_type, [])
            if expected_options and correct_answer in expected_options:
                if user_answer in expected_options:
                    return "wrong_option"  # eligió una opción válida pero incorrecta
                else:
                    return "pattern_mismatch"  # ni siquiera eligió una opción válida
        return "wrong_option"


    elif skill_type == "memory_number":
        # Memory: compare submitted length vs expected length
        if user_answer is not None and correct_answer is not None:
            try:
                user_len = len(user_answer)
                correct_len = len(correct_answer)
                if user_len != correct_len:
                    return "sequence_error"
                # Same length but wrong positions
                return "position_error"
            except (TypeError, ValueError):
                pass
        return "position_error"

    return "careless"


def record_error(
    db: DBSession,
    *,
    skill_id: int,
    skill_type: str,
    session_id: int,
    round_id: int,
    attempt_id: int,
    is_correct: bool,
    user_answer=None,
    correct_answer=None,
    puzzle_type: Optional[str] = None,
    response_time_ms: Optional[int] = None,
    level: int = 1,
    error_detail: Optional[str] = None,
) -> Optional[LearningPattern]:
    """Record an error pattern for an incorrect attempt. No-op if correct.

    Returns the created LearningPattern, or None if the attempt was correct.
    """
    error_type = classify_error(
        skill_type, is_correct,
        user_answer=user_answer, correct_answer=correct_answer,
        puzzle_type=puzzle_type, response_time_ms=response_time_ms,
    )
    if error_type is None:
        return None

    # 1. Store raw learning pattern
    pattern = LearningPattern(
        skill_id=skill_id,
        skill_type=skill_type,
        session_id=session_id,
        round_id=round_id,
        attempt_id=attempt_id,
        error_type=error_type,
        error_detail=error_detail,
        level=level,
    )
    db.add(pattern)
    db.flush()

    # 2. Upsert error pattern aggregation
    stmt = select(ErrorPattern).where(
        ErrorPattern.skill_id == skill_id,
        ErrorPattern.error_type == error_type,
    )
    existing = db.exec(stmt).first()

    if existing:
        existing.count += 1
        # Severity: ratio of this error type to total errors (capped at 1.0)
        total_errors = db.exec(
            select(func.sum(ErrorPattern.count)).where(ErrorPattern.skill_id == skill_id)
        ).one()
        existing.severity = min(existing.count / max(total_errors or 1, 1), 1.0)
        existing.last_seen = datetime.now(timezone.utc)
        db.add(existing)
    else:
        ep = ErrorPattern(
            skill_id=skill_id,
            skill_type=skill_type,
            error_type=error_type,
            count=1,
            severity=0.1,
        )
        db.add(ep)
        db.flush()

    # 3. Link session to error pattern
    se = SessionError(
        session_id=session_id,
        session_type=skill_type,
        error_pattern_id=existing.id if existing else ep.id,
        confidence=1.0,
    )
    db.add(se)
    db.flush()

    return pattern


def get_sliding_window(
    db: DBSession,
    skill_id: int,
    limit: int = 25,
) -> list[dict]:
    """Get last N learning patterns for a skill (sliding window for AI prompts).

    Returns a list of dicts with error_type, error_detail, level, created_at.
    Used to inject into AI prompts for adaptive problem generation.
    """
    stmt = (
        select(LearningPattern)
        .where(LearningPattern.skill_id == skill_id)
        .order_by(LearningPattern.created_at.desc(), LearningPattern.id.desc())
        .limit(limit)
    )
    patterns = db.exec(stmt).all()

    return [
        {
            "error_type": p.error_type,
            "error_detail": p.error_detail,
            "level": p.level,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in patterns
    ]


def get_error_summary(
    db: DBSession,
    skill_id: int,
) -> list[dict]:
    """Get aggregated error patterns for a skill (for prompt injection).

    Returns error types sorted by severity (highest first).
    """
    stmt = (
        select(ErrorPattern)
        .where(ErrorPattern.skill_id == skill_id)
        .order_by(ErrorPattern.severity.desc())
    )
    patterns = db.exec(stmt).all()

    return [
        {
            "error_type": p.error_type,
            "count": p.count,
            "severity": round(p.severity, 2),
            "description": ERROR_TYPES.get(p.skill_type, {}).get(p.error_type, p.error_type),
        }
        for p in patterns
    ]


def format_patterns_for_prompt(
    db: DBSession,
    skill_id: int,
    skill_type: str,
) -> str:
    """Format error patterns as a concise string for AI prompt injection.

    Returns empty string if no patterns exist (graceful degradation).
    """
    summary = get_error_summary(db, skill_id)
    if not summary:
        return ""

    lines = ["Patrones de error del usuario (últimas sesiones):"]
    for item in summary[:5]:  # Top 5 error types
        lines.append(
            f"- {item['description']}: {item['count']} veces "
            f"(severidad: {item['severity']})"
        )

    # Add sliding window context
    window = get_sliding_window(db, skill_id, limit=10)
    if window:
        recent_types = [w["error_type"] for w in window]
        from collections import Counter
        most_common = Counter(recent_types).most_common(3)
        if most_common:
            lines.append("Errores más recientes:")
            for error_type, count in most_common:
                desc = ERROR_TYPES.get(skill_type, {}).get(error_type, error_type)
                lines.append(f"  - {desc}: {count} en últimas 10 oportunidades")

    return "\n".join(lines)
