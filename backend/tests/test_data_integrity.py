"""
Data integrity tests for Phase 5 — FK enforcement, cascade, constraints,
orphan cleanup, and PRAGMA activation.

All tests depend on the PRAGMA foreign_keys=ON being active, which is
enabled in core/database.py's _set_sqlite_pragma() callback. The conftest
uses StaticPool so the listen event fires once per test class.

Test coverage (T-10 through T-14):
  - T-10: PRAGMA foreign_keys returns 1
  - T-11: Bad FK INSERT raises IntegrityError
  - T-12: Cascade delete (SkillLevelHistory, CognitiveSession→CognitiveTrial,
          SessionError)
  - T-13: ErrorPattern UNIQUE constraint violation
  - T-14: Orphan cleanup idempotency
"""

import importlib
from datetime import datetime, timezone

import pytest
from sqlalchemy import text
from sqlmodel import Session, delete, select

# =============================================================================
# T-10: PRAGMA + FK enforcement
# =============================================================================


def test_pragma_active(engine):
    """PRAGMA foreign_keys MUST return 1 after database initialization."""
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA foreign_keys")).scalar()
    assert result == 1, (
        f"Expected PRAGMA foreign_keys=1, got {result}. "
        "Check _set_sqlite_pragma() in core/database.py"
    )


# Use a direct connection — bypassing the session so we can use PRAGMA directly
def test_bad_fk_raises_integrity_error(engine):
    """INSERT with non-existent FK reference MUST raise IntegrityError."""
    from models.models import Skill

    # Create a skill first so we know a valid ID
    with Session(engine) as session:
        skill = Skill(
            slug="fk-test",
            name="FK Test",
            domain="test",
            skill_type="test",
            config_path="test.yaml",
        )
        session.add(skill)
        session.commit()
        valid_skill_id = skill.id

        # Now try inserting a session with a non-existent skill_id
        with Session(engine) as session:
            # Use raw SQL to bypass ORM and hit the constraint directly
            bad_id = valid_skill_id + 9999
            stmt = text(
                "INSERT INTO session "
                "(skill_id, duration_minutes, what_i_practiced, difficulty, "
                " entry_mode, ai_fields_status, created_at) "
                "VALUES (:sid, 10, 'test', 3, 'quick', 'pending', :ts)"
            )
            with pytest.raises(Exception) as excinfo:
                session.execute(
                    stmt,
                    {
                        "sid": bad_id,
                        "ts": datetime.now(timezone.utc).isoformat(),
                    },
                )
                session.commit()

            # Verify it's an IntegrityError (or subclass)
            error_name = type(excinfo.value).__name__
            assert "IntegrityError" in error_name or "integrity" in str(
                excinfo.value
            ).lower(), (
                f"Expected IntegrityError, got {error_name}: {excinfo.value}"
            )


# =============================================================================
# T-11: Cascade delete tests
# =============================================================================


def test_cascade_skilllevelhistory(engine):
    """Deleting a Skill cascades to its SkillLevelHistory rows."""
    from models.models import Skill, SkillLevelHistory

    with Session(engine) as session:
        skill = Skill(
            slug="cascade-slh",
            name="Cascade SLH",
            domain="test",
            skill_type="test",
            config_path="test.yaml",
        )
        session.add(skill)
        session.commit()
        skill_id = skill.id

        slh = SkillLevelHistory(
            skill_id=skill_id,
            success=True,
            level_before=1.0,
            level_after=2.0,
            delta=1.0,
            trigger="test",
        )
        session.add(slh)
        session.commit()
        slh_id = slh.id

        # Delete the skill
        session.exec(delete(Skill).where(Skill.id == skill_id))
        session.commit()

        # Verify SkillLevelHistory is gone
        remaining = session.exec(
            select(SkillLevelHistory).where(SkillLevelHistory.id == slh_id)
        ).first()
        assert remaining is None, (
            f"SkillLevelHistory {slh_id} should have been cascade-deleted"
        )


def test_cascade_cognitivesession_cognitivetrial(engine):
    """Deleting a CognitiveSession cascades to its CognitiveTrials."""
    from models.cognitive_models import CognitiveSession, CognitiveSkill, CognitiveTrial

    with Session(engine) as session:
        skill = CognitiveSkill(
            nombre="Test",
            descripcion="Test",
            fase_iq_base=100,
        )
        session.add(skill)
        session.commit()

        cs = CognitiveSession(
            cognitive_skill_id=skill.id,
        )
        session.add(cs)
        session.commit()
        cs_id = cs.id

        ct = CognitiveTrial(
            session_id=cs_id,
            estimulo="test",
            respuesta_esperada="A",
            respuesta_usuario="A",
            es_correcto=True,
            tiempo_reaccion_ms=500,
        )
        session.add(ct)
        session.commit()
        ct_id = ct.id

        # Delete the CognitiveSession
        session.exec(
            delete(CognitiveSession).where(CognitiveSession.id == cs_id)
        )
        session.commit()

        # Verify CognitiveTrial is gone
        remaining = session.exec(
            select(CognitiveTrial).where(CognitiveTrial.id == ct_id)
        ).first()
        assert remaining is None, (
            f"CognitiveTrial {ct_id} should have been cascade-deleted"
        )


def test_sessionerror_discriminator_no_fk(engine):
    """SessionError.session_id is a discriminator — no FK enforcement.

    It can reference maththinkingsession, memorynumbersession, or
    iqpracticesession depending on session_type. Since no single FK
    is possible, deleting a consolidated Session must NOT cascade.
    """
    from models.models import (
        ErrorPattern,
        SessionError,
        Skill,
    )
    from models.models import (
        Session as PracticeSession,
    )

    with Session(engine) as session:
        skill = Skill(
            slug="discriminator-se",
            name="Discriminator SE",
            domain="test",
            skill_type="test",
            config_path="test.yaml",
        )
        session.add(skill)
        session.commit()

        ps = PracticeSession(
            skill_id=skill.id,
            duration_minutes=10,
            what_i_practiced="test discriminator",
            difficulty=3,
            entry_mode="quick",
            ai_fields_status="pending",
        )
        session.add(ps)
        session.commit()

        ep = ErrorPattern(
            skill_id=skill.id,
            skill_type="memory_number",
            error_type="test",
        )
        session.add(ep)
        session.commit()

        # session_id uses a game session ID (mocked), NOT consolidated session.id
        se = SessionError(
            session_id=ps.id,  # This is a game session ID, not session.id
            session_type="memory_number",
            error_pattern_id=ep.id,
            confidence=1.0,
        )
        session.add(se)
        session.commit()
        se_id = se.id

        # Delete the consolidated Session — must NOT cascade to SessionError
        # because session_id is a discriminator field without FK
        session.exec(
            delete(PracticeSession).where(PracticeSession.id == ps.id)
        )
        session.commit()

        remaining = session.exec(
            select(SessionError).where(SessionError.id == se_id)
        ).first()
        assert remaining is not None, (
            "SessionError should survive consolidated Session deletion — "
            "discriminator field has no FK cascade"
        )


# =============================================================================
# T-12: ErrorPattern UNIQUE constraint
# =============================================================================


def test_errorpattern_unique_constraint(engine):
    """Duplicate (skill_id, error_type) MUST raise IntegrityError."""
    from models.models import ErrorPattern, Skill

    with Session(engine) as session:
        skill = Skill(
            slug="unique-ep",
            name="Unique EP",
            domain="test",
            skill_type="test",
            config_path="test.yaml",
        )
        session.add(skill)
        session.commit()
        skill_id = skill.id

        # First insert must succeed
        ep1 = ErrorPattern(
            skill_id=skill_id,
            skill_type="memory_number",
            error_type="duplicate_test",
            count=1,
            severity=0.5,
        )
        session.add(ep1)
        session.commit()

        # Second insert with same (skill_id, error_type) must fail
        ep2 = ErrorPattern(
            skill_id=skill_id,
            skill_type="memory_number",
            error_type="duplicate_test",
            count=2,
            severity=0.8,
        )
        session.add(ep2)
        with pytest.raises(Exception) as excinfo:
            session.commit()

        error_name = type(excinfo.value).__name__
        assert "IntegrityError" in error_name or "integrity" in str(
            excinfo.value
        ).lower(), (
            f"Expected IntegrityError for duplicate ErrorPattern, "
            f"got {error_name}: {excinfo.value}"
        )


# =============================================================================
# T-13: Orphan cleanup idempotency
# =============================================================================


def test_orphan_cleanup_idempotent(engine, monkeypatch):
    """Migration 006 destructive mode removes orphans; re-run finds zero."""
    from models.models import ErrorPattern, Skill

    # Ensure DRY_RUN is off for this test
    monkeypatch.setenv("DRY_RUN", "0")

    # 1. Insert a skill with an error pattern
    with Session(engine) as session:
        skill = Skill(
            slug="orphan-test",
            name="Orphan Test",
            domain="test",
            skill_type="test",
            config_path="test.yaml",
        )
        session.add(skill)
        session.commit()
        skill_id = skill.id

        ep = ErrorPattern(
            skill_id=skill_id,
            skill_type="memory_number",
            error_type="orphan_test",
        )
        session.add(ep)
        session.commit()

    # 2. Disable FK enforcement temporarily to create orphans without
    #    cascade deletion. Then delete the skill so errorpattern becomes orphaned.
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        conn.execute(
            text("DELETE FROM skill WHERE id = :sid"), {"sid": skill_id}
        )

    # 3. Confirm orphans exist
    with engine.begin() as conn:
        orphan_count = conn.execute(
            text(
                "SELECT COUNT(*) FROM errorpattern WHERE skill_id = :sid"
            ),
            {"sid": skill_id},
        ).scalar()
    assert orphan_count > 0, "Expected orphans before cleanup"

    # 4. Run migration 006 destructive
    m006 = importlib.import_module("migrations.006_fk_orphan_cleanup")
    m006_up = m006.up

    with engine.begin() as conn:
        m006_up(conn)

    # 5. Verify orphans are gone
    with engine.begin() as conn:
        remaining = conn.execute(
            text(
                "SELECT COUNT(*) FROM errorpattern WHERE skill_id = :sid"
            ),
            {"sid": skill_id},
        ).scalar()
    assert remaining == 0, (
        f"Expected 0 orphans after cleanup, got {remaining}"
    )

    # 6. Re-run — must be idempotent (zero orphans to delete)
    with engine.begin() as conn:
        m006_up(conn)  # must not raise


# =============================================================================
# T-14: LearningPattern index existence
# =============================================================================


def test_learningpattern_indexes_exist(engine):
    """LearningPattern MUST have indexes on session_id, round_id, attempt_id."""
    with engine.connect() as conn:
        indexes = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='index'")
        ).fetchall()

    index_names = {row[0] for row in indexes}

    # SQLModel's index=True generates names like ix_learningpattern_session_id
    assert any(
        "session_id" in name and "learningpattern" in name
        for name in index_names
    ), (
        f"No session_id index found on learningpattern. "
        f"Available indexes: {sorted(index_names)}"
    )
    assert any(
        "round_id" in name and "learningpattern" in name
        for name in index_names
    ), (
        f"No round_id index found on learningpattern. "
        f"Available indexes: {sorted(index_names)}"
    )
    assert any(
        "attempt_id" in name and "learningpattern" in name
        for name in index_names
    ), (
        f"No attempt_id index found on learningpattern. "
        f"Available indexes: {sorted(index_names)}"
    )
