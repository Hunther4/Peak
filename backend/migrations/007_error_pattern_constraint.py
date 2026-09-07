"""007 — Add UNIQUE(skill_id, error_type) constraint to errorpattern.

Recreates the errorpattern table via CREATE TABLE AS + DROP + RENAME to add
the uniqueness constraint. SQLite does not support ALTER TABLE ADD CONSTRAINT,
so this is the only safe approach that works on all SQLite versions.

Also deduplicates existing data, keeping only the lowest-id row per
(skill_id, error_type) pair.
"""

import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)


def up(conn):
    """Recreate errorpattern with UNIQUE(skill_id, error_type)."""

    # 1. Check if constraint already exists
    existing = {
        row[1]
        for row in conn.execute(
            text("SELECT * FROM sqlite_master WHERE name LIKE 'uq_errorpattern%'")
        ).fetchall()
    }
    if existing:
        logger.info(
            "UNIQUE constraint already exists on errorpattern — skipping"
        )
        return

    # 2. Deduplicate: keep lowest id per (skill_id, error_type)
    conn.execute(text("""
        DELETE FROM errorpattern
        WHERE id NOT IN (
            SELECT MIN(id) FROM errorpattern
            GROUP BY skill_id, error_type
        )
    """))

    # 3. Create new table with UNIQUE constraint
    conn.execute(text("""
        CREATE TABLE errorpattern_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER NOT NULL REFERENCES skill(id) ON DELETE CASCADE,
            skill_type VARCHAR NOT NULL,
            error_type VARCHAR NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            severity FLOAT NOT NULL DEFAULT 0.0,
            last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(skill_id, error_type)
        )
    """))

    # 4. Copy existing data
    conn.execute(text("""
        INSERT INTO errorpattern_new (id, skill_id, skill_type, error_type,
                                      count, severity, last_seen, created_at)
        SELECT id, skill_id, skill_type, error_type,
               count, severity, last_seen, created_at
        FROM errorpattern
    """))

    # 5. Drop old table and rename new one
    conn.execute(text("DROP TABLE errorpattern"))
    conn.execute(text("ALTER TABLE errorpattern_new RENAME TO errorpattern"))

    logger.info("errorpattern table recreated with UNIQUE(skill_id, error_type)")


MIGRATION = {
    "version": 7,
    "name": "error_pattern_constraint",
    "up": up,
}
