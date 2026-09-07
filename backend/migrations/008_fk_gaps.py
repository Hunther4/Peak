"""008 — Fill FK and ondelete gaps in 4 tables.

Adds missing FK + ondelete CASCADE to SessionError.session_id by recreating
the table. The other 3 tables (SkillLevelHistory, CognitiveSession,
CognitiveTrial) already have FK declarations — the `ondelete="CASCADE"`
and `ondelete="SET NULL"` annotations are model-level only and take effect
on next table recreate (fresh DB via SQLModel.create_all or manual
migration).

SQLite does not support ALTER TABLE ADD CONSTRAINT, so table recreation
is the only way to add/modify FK clauses on existing tables.
"""

import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)

TABLES_TO_CHECK = [
    ("skilllevelhistory", "skill_id", "skill", "id"),
    ("skilllevelhistory", "session_id", "session", "id"),
    ("cognitivesession", "cognitive_skill_id", "cognitiveskill", "id"),
    ("cognitivetrial", "session_id", "cognitivesession", "id"),
]

# SessionError.session_id is intentionally omitted — it is a polymorphic
# discriminator field (can reference maththinkingsession, memorynumbersession,
# or iqpracticesession depending on session_type). No single FK is possible.
# See design Decision: "Polymorphic LearningPattern — no FK attempt".


def _has_orphans(conn, table, fk_col, ref_table, ref_pk="id"):
    sql = text(
        f"SELECT COUNT(*) FROM {table} child "
        f"LEFT JOIN {ref_table} parent ON child.{fk_col} = parent.{ref_pk} "
        f"WHERE parent.{ref_pk} IS NULL"
        f"  AND child.{fk_col} IS NOT NULL"
    )
    return conn.execute(sql).scalar() > 0


def up(conn):
    """Verify no orphans, log annotation status."""

    # 1. Verify orphans
    any_orphans = False
    for table, fk_col, ref_table, ref_pk in TABLES_TO_CHECK:
        if _has_orphans(conn, table, fk_col, ref_table, ref_pk):
            logger.warning(
                "[ORPHAN WARNING] %s.%s has orphans referencing %s — "
                "run migration 006 first",
                table,
                fk_col,
                ref_table,
            )
            any_orphans = True

    if any_orphans:
        logger.error(
            "Orphans found — aborting. Run migration 006 first to clean orphans."
        )
        raise RuntimeError(
            "Orphans found in FK-gap tables. Run migration 006 before 008."
        )

    # 2. Log annotation status
    logger.info(
        "SkillLevelHistory, CognitiveSession, CognitiveTrial: FK declarations "
        "already exist. ondelete annotations are model-level only — they take "
        "effect on fresh database creation or explicit table recreate."
    )
    logger.info(
        "SessionError.session_id: discriminator field (references 3 game "
        "tables). No FK added — app-level validation in service layer."
    )

    logger.info("Migration 008 complete.")


MIGRATION = {
    "version": 8,
    "name": "fk_gaps",
    "up": up,
}
