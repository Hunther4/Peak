"""006 — Orphan cleanup before enabling PRAGMA foreign_keys=ON.

Scans all FK-referencing tables for orphan rows (rows whose FK target does
not exist) and optionally deletes them. Supports DRY_RUN=1 environment mode.

This migration MUST run *before* PRAGMA foreign_keys=ON becomes part of normal
operation, because FK enforcement would reject INSERTS that reference deleted
parents. However, the PRAGMA is already being set in _set_sqlite_pragma() —
this migration cleans existing data so that existing orphans don't cause
startup failures once enforcement is active.
"""

import logging
import os

from sqlalchemy import text

logger = logging.getLogger(__name__)

# fmt: off
# (child_table, fk_column, parent_table, parent_pk)
FK_PAIRS = [
    # session → skill
    ("session",             "skill_id",               "skill",                 "id"),
    # assessment → skill, session
    ("assessment",          "skill_id",               "skill",                 "id"),
    ("assessment",          "linked_session_id",      "session",               "id"),
    # mentalrep → skill
    ("mentalrep",           "skill_id",               "skill",                 "id"),
    # challenge → skill, assessment
    ("challenge",           "skill_id",               "skill",                 "id"),
    ("challenge",           "linked_assessment_id",   "assessment",            "id"),
    # memorynumbersession → skill, session
    ("memorynumbersession",       "skill_id",               "skill",                 "id"),
    ("memorynumbersession",       "consolidated_session_id", "session",             "id"),
    # memorynumberround → memorynumbersession
    ("memorynumberround",         "game_session_id",        "memorynumbersession",   "id"),
    # memorynumberattempt → memorynumberround
    ("memorynumberattempt",       "round_id",               "memorynumberround",     "id"),
    # maththinkingsession → skill, session
    ("maththinkingsession",       "skill_id",               "skill",                 "id"),
    ("maththinkingsession",       "consolidated_session_id", "session",             "id"),
    # maththinkinground → maththinkingsession
    ("maththinkinground",         "session_id",             "maththinkingsession",   "id"),
    # maththinkingattempt → maththinkinground
    ("maththinkingattempt",       "round_id",               "maththinkinground",     "id"),
    # iqpracticesession → skill, session
    ("iqpracticesession",         "skill_id",               "skill",                 "id"),
    ("iqpracticesession",         "consolidated_session_id", "session",             "id"),
    # iqpracticeround → iqpracticesession
    ("iqpracticeround",           "session_id",             "iqpracticesession",     "id"),
    # iqpracticeattempt → iqpracticeround
    ("iqpracticeattempt",         "round_id",               "iqpracticeround",       "id"),
    # learningpattern → skill
    ("learningpattern",     "skill_id",               "skill",                 "id"),
    # errorpattern → skill
    ("errorpattern",        "skill_id",               "skill",                 "id"),
    # skill → skill (self-referencing parent_id)
    ("skill",               "parent_id",              "skill",                 "id"),
    # sessionerror → errorpattern
    ("sessionerror",        "error_pattern_id",       "errorpattern",          "id"),
    # skilllevelhistory → skill, session
    ("skilllevelhistory",   "skill_id",               "skill",                 "id"),
    ("skilllevelhistory",   "session_id",             "session",               "id"),
    # cognitivesession → cognitiveskill, session
    ("cognitivesession",    "cognitive_skill_id",        "cognitiveskill",        "id"),
    ("cognitivesession",    "consolidated_session_id",   "session",               "id"),
    # cognitivetrial → cognitivesession
    ("cognitivetrial",      "session_id",             "cognitivesession",      "id"),
    # memorysessionmeta → memorynumbersession
    ("memorysessionmeta",   "game_session_id",        "memorynumbersession",   "id"),
    # memorystrategylog → memorynumbersession, memorynumberround
    ("memorystrategylog",   "game_session_id",        "memorynumbersession",   "id"),
    ("memorystrategylog",   "round_id",               "memorynumberround",     "id"),
]
# fmt: on


def _count_orphans(conn, table, fk_col, ref_table, ref_pk="id"):
    """Return (count, orphan_rowids)."""
    sql = text(
        f"SELECT child.rowid FROM {table} child "
        f"LEFT JOIN {ref_table} parent ON child.{fk_col} = parent.{ref_pk} "
        f"WHERE parent.{ref_pk} IS NULL"
        f"  AND child.{fk_col} IS NOT NULL"
    )
    rows = conn.execute(sql).fetchall()
    return len(rows), [r[0] for r in rows]


def _delete_orphans(conn, table, rowids):
    """Delete orphans by rowid."""
    if not rowids:
        return
    placeholders = ",".join(str(rid) for rid in rowids)
    conn.execute(text(f"DELETE FROM {table} WHERE rowid IN ({placeholders})"))


def up(conn):
    """Scan all FK pairs, log orphans, delete in destructive mode."""
    dry_run = os.environ.get("DRY_RUN", "0") == "1"
    mode = "DRY RUN (no changes)" if dry_run else "DESTRUCTIVE"

    total_orphans = 0
    for table, fk_col, ref_table, ref_pk in FK_PAIRS:
        count, rowids = _count_orphans(conn, table, fk_col, ref_table, ref_pk)
        if count == 0:
            continue

        total_orphans += count
        logger.warning(
            "[%s] %s.%s → %s: %d orphan(s) — rowids=%s",
            mode,
            table,
            fk_col,
            ref_table,
            count,
            rowids,
        )

        if not dry_run:
            _delete_orphans(conn, table, rowids)
            logger.info("[DESTRUCTIVE] Deleted %d orphans from %s", count, table)

    if total_orphans == 0:
        logger.info("[%s] Zero orphans found across all FK pairs", mode)

    logger.info(
        "[%s] Orphan scan complete. Total orphans: %d", mode, total_orphans
    )


MIGRATION = {
    "version": 6,
    "name": "fk_orphan_cleanup",
    "up": up,
}
