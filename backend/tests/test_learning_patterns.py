"""Tests for the learning patterns system.

Covers:
- Error extraction (record_error / classify_error)
- ErrorPattern aggregation (upsert + severity)
- Sliding window query (get_sliding_window)
- Prompt injection (format_patterns_for_prompt)
"""

import pytest
from sqlmodel import Session, func, select

from models.models import ErrorPattern, LearningPattern, SessionError
from services.learning_patterns_service import (
    ERROR_TYPES,
    classify_error,
    format_patterns_for_prompt,
    get_sliding_window,
    record_error,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_skill(session: Session, slug: str = "lp-test-skill") -> int:
    """Create a Skill row and return its id. Caller is responsible for commit."""
    from models.models import Skill

    skill = Skill(
        slug=slug,
        name=f"Skill {slug}",
        domain="memory",
        skill_type="staircase",
        config_path="skills/test.yaml",
        current_level=1.0,
    )
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill.id


# ---------------------------------------------------------------------------
# 1. Error Extraction (record_error / classify_error)
# ---------------------------------------------------------------------------


class TestRecordError:
    """record_error: extracts the error and persists a LearningPattern row."""

    def test_record_error_creates_learning_pattern(self, session):
        skill_id = _create_skill(session, slug="lp-record-creates")
        result = record_error(
            session,
            skill_id=skill_id,
            skill_type="problem_set",
            session_id=1,
            round_id=1,
            attempt_id=1,
            is_correct=False,
            user_answer=15,
            correct_answer=10,
            level=2,
            error_detail="Said 15 instead of 10",
        )
        session.commit()

        assert result is not None
        assert result.id is not None
        assert result.skill_id == skill_id
        assert result.skill_type == "problem_set"
        assert result.error_type == "arithmetic"
        assert result.level == 2
        assert result.error_detail == "Said 15 instead of 10"

        # Verify it is actually persisted
        rows = session.exec(
            select(LearningPattern).where(LearningPattern.skill_id == skill_id)
        ).all()
        assert len(rows) == 1

    def test_record_error_returns_none_for_correct(self, session):
        skill_id = _create_skill(session, slug="lp-record-correct")
        result = record_error(
            session,
            skill_id=skill_id,
            skill_type="problem_set",
            session_id=1,
            round_id=1,
            attempt_id=1,
            is_correct=True,
            user_answer=10,
            correct_answer=10,
        )
        session.commit()

        assert result is None

        # Nothing should be persisted
        rows = session.exec(
            select(LearningPattern).where(LearningPattern.skill_id == skill_id)
        ).all()
        assert rows == []


class TestClassifyError:
    """classify_error: pure function — returns the right bucket per skill_type."""

    def test_classify_problem_set_arithmetic(self):
        # user_answer=15, correct=10 → diff=5, >10% of 10 → arithmetic
        result = classify_error(
            "problem_set",
            is_correct=False,
            user_answer=15,
            correct_answer=10,
        )
        assert result == "arithmetic"

    def test_classify_problem_set_careless(self):
        # user_answer=10.5, correct=10 → diff=0.5, <10% of 10 → careless
        result = classify_error(
            "problem_set",
            is_correct=False,
            user_answer=10.5,
            correct_answer=10,
        )
        assert result == "careless"

    def test_classify_iq_practice_wrong_option(self):
        result = classify_error(
            "iq_practice",
            is_correct=False,
            user_answer="B",
            correct_answer="C",
        )
        assert result == "wrong_option"

    def test_classify_memory_number_position_error(self):
        result = classify_error(
            "memory_number",
            is_correct=False,
            user_answer="1234",
            correct_answer="4321",
        )
        assert result == "position_error"

    def test_classify_timeout(self):
        # response_time_ms > 30000 wins for any skill_type
        for skill in ("problem_set", "iq_practice", "memory_number"):
            result = classify_error(
                skill,
                is_correct=False,
                response_time_ms=31000,
            )
            assert result == "timeout", f"timeout failed for skill={skill}"

    def test_classify_correct_returns_none(self):
        result = classify_error("problem_set", is_correct=True)
        assert result is None


# ---------------------------------------------------------------------------
# 2. Aggregation (ErrorPattern upsert + severity)
# ---------------------------------------------------------------------------


class TestErrorPatternUpsert:
    """ErrorPattern aggregation: count and severity are updated on each error."""

    def test_error_pattern_new_type(self, session):
        skill_id = _create_skill(session, slug="lp-agg-new")
        record_error(
            session,
            skill_id=skill_id,
            skill_type="iq_practice",
            session_id=1,
            round_id=1,
            attempt_id=1,
            is_correct=False,
        )
        session.commit()

        rows = session.exec(
            select(ErrorPattern).where(ErrorPattern.skill_id == skill_id)
        ).all()
        assert len(rows) == 1
        assert rows[0].error_type == "wrong_option"
        assert rows[0].count == 1
        # New row gets a default severity of 0.1
        assert rows[0].severity == 0.1

    def test_error_pattern_upsert_increments(self, session):
        skill_id = _create_skill(session, slug="lp-agg-increments")
        # First error of type
        record_error(
            session,
            skill_id=skill_id,
            skill_type="iq_practice",
            session_id=1,
            round_id=1,
            attempt_id=1,
            is_correct=False,
        )
        # Second error of the same type
        record_error(
            session,
            skill_id=skill_id,
            skill_type="iq_practice",
            session_id=1,
            round_id=2,
            attempt_id=2,
            is_correct=False,
        )
        session.commit()

        rows = session.exec(
            select(ErrorPattern).where(ErrorPattern.skill_id == skill_id)
        ).all()
        assert len(rows) == 1, "expected a single aggregated row, not duplicates"
        assert rows[0].count == 2
        # Only one SessionError link per record_error call
        links = session.exec(
            select(SessionError).where(SessionError.session_id == 1)
        ).all()
        assert len(links) == 2

    def test_error_pattern_severity_calculation(self, session):
        """severity = count / total_errors for that skill (capped at 1.0)."""
        skill_id = _create_skill(session, slug="lp-agg-severity")

        # First error: type A → count=1, total=1, severity=1.0 (recalculated)
        record_error(
            session,
            skill_id=skill_id,
            skill_type="iq_practice",
            session_id=1,
            round_id=1,
            attempt_id=1,
            is_correct=False,
        )
        # Second error: type B → count=1, total=2, severity=0.5
        record_error(
            session,
            skill_id=skill_id,
            skill_type="iq_practice",
            session_id=2,
            round_id=1,
            attempt_id=1,
            is_correct=False,
        )
        # Third error: type A again → count=2, total=3, severity=2/3
        record_error(
            session,
            skill_id=skill_id,
            skill_type="iq_practice",
            session_id=3,
            round_id=1,
            attempt_id=1,
            is_correct=False,
        )
        session.commit()

        rows = session.exec(
            select(ErrorPattern).where(ErrorPattern.skill_id == skill_id)
            .order_by(ErrorPattern.error_type)
        ).all()
        by_type = {r.error_type: r for r in rows}

        assert set(by_type.keys()) == {"wrong_option"}
        ep = by_type["wrong_option"]
        # All 3 attempts share the same error_type (iq_practice → wrong_option)
        assert ep.count == 3
        # total_errors = 3, so severity = 3/3 = 1.0
        assert ep.severity == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 3. Sliding Window (get_sliding_window)
# ---------------------------------------------------------------------------


class TestSlidingWindow:
    """get_sliding_window: returns last N patterns ordered by date desc."""

    def test_sliding_window_returns_last_25(self, session):
        skill_id = _create_skill(session, slug="lp-window-25")

        for i in range(30):
            record_error(
                session,
                skill_id=skill_id,
                skill_type="iq_practice",
                session_id=i,
                round_id=i,
                attempt_id=i,
                is_correct=False,
            )
        session.commit()

        window = get_sliding_window(session, skill_id, limit=25)
        assert len(window) == 25

        # All entries are dicts with the documented shape
        for entry in window:
            assert set(entry.keys()) == {"error_type", "error_detail", "level", "created_at"}
            assert entry["error_type"] == "wrong_option"

        # Verify total is 30 but window caps at 25
        total = session.exec(
            select(func.count(LearningPattern.id)).where(
                LearningPattern.skill_id == skill_id
            )
        ).one()
        assert total == 30

    def test_sliding_window_empty(self, session):
        skill_id = _create_skill(session, slug="lp-window-empty")
        window = get_sliding_window(session, skill_id, limit=25)
        assert window == []

    def test_sliding_window_ordered_by_date(self, session):
        skill_id = _create_skill(session, slug="lp-window-ordered")

        for i in range(10):
            record_error(
                session,
                skill_id=skill_id,
                skill_type="iq_practice",
                session_id=i,
                round_id=i,
                attempt_id=i,
                is_correct=False,
                level=i + 1,
            )
        session.commit()

        window = get_sliding_window(session, skill_id, limit=10)
        assert len(window) == 10

        # Most-recent first — the last record_error (level=10) should be at index 0
        levels = [entry["level"] for entry in window]
        assert levels[0] == 10
        assert levels[-1] == 1
        assert levels == sorted(levels, reverse=True)


# ---------------------------------------------------------------------------
# 4. Prompt Injection (format_patterns_for_prompt)
# ---------------------------------------------------------------------------


class TestFormatPatternsForPrompt:
    """format_patterns_for_prompt: builds a string the AI can consume."""

    def test_format_patterns_empty(self, session):
        skill_id = _create_skill(session, slug="lp-format-empty")
        result = format_patterns_for_prompt(session, skill_id, "problem_set")
        assert result == ""

    def test_format_patterns_with_data(self, session):
        skill_id = _create_skill(session, slug="lp-format-data")

        # Two arithmetic errors
        for i in range(2):
            record_error(
                session,
                skill_id=skill_id,
                skill_type="problem_set",
                session_id=100 + i,
                round_id=1,
                attempt_id=1,
                is_correct=False,
                user_answer=15,
                correct_answer=10,
                error_detail="Said 15 instead of 10",
            )
        session.commit()

        result = format_patterns_for_prompt(session, skill_id, "problem_set")
        assert result != ""
        # Header in Spanish
        assert "Patrones de error" in result
        # Description for arithmetic error type
        assert ERROR_TYPES["problem_set"]["arithmetic"] in result
        # Count and severity
        assert "2 veces" in result
        assert "severidad" in result

    def test_format_patterns_includes_recent(self, session):
        skill_id = _create_skill(session, slug="lp-format-recent")

        # Insert 12 errors → sliding window (limit=10) is queried internally
        for i in range(12):
            record_error(
                session,
                skill_id=skill_id,
                skill_type="iq_practice",
                session_id=200 + i,
                round_id=1,
                attempt_id=1,
                is_correct=False,
            )
        session.commit()

        result = format_patterns_for_prompt(session, skill_id, "iq_practice")
        assert result != ""
        # The "Errores más recientes" block is appended when window has entries
        assert "Errores más recientes" in result
        assert "wrong_option" in result or ERROR_TYPES["iq_practice"]["wrong_option"] in result
        # The recent block references the window size explicitly
        assert "últimas 10" in result
