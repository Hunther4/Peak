"""005 — Skill hierarchy + adaptive staircase + level history.

Adds parent-child skill relationships, practice level tracking,
and a level history table for the adaptive staircase algorithm.

Tables:
  - skilllevelhistory: every staircase evaluation (success/failure + level delta)

Columns added to skill:
  - parent_id: self-referencing FK for skill hierarchy
  - practice_level: naive | purposeful | deliberate (last computed value)
"""

from sqlalchemy import text


def up(conn):
    """Add hierarchy fields to skill and create level history table."""

    # 1. Add parent_id and practice_level to skill
    # SQLite ADD COLUMN is idempotent if column exists (errors), so guard:
    cols = {row[1] for row in conn.execute(text("PRAGMA table_info(skill)")).fetchall()}

    if "parent_id" not in cols:
        conn.execute(text("ALTER TABLE skill ADD COLUMN parent_id INTEGER REFERENCES skill(id) ON DELETE SET NULL"))

    if "practice_level" not in cols:
        conn.execute(text("ALTER TABLE skill ADD COLUMN practice_level VARCHAR(20)"))

    # 2. Create skilllevelhistory table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS skilllevelhistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER NOT NULL REFERENCES skill(id),
            success BOOLEAN NOT NULL,
            level_before REAL NOT NULL,
            level_after REAL NOT NULL,
            delta REAL NOT NULL,
            trigger VARCHAR(50) NOT NULL,
            session_id INTEGER REFERENCES session(id) ON DELETE SET NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # 3. Indexes
    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_skilllevelhistory_skill_id "
        "ON skilllevelhistory(skill_id)"
    ))
    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_skilllevelhistory_created_at "
        "ON skilllevelhistory(created_at)"
    ))
    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_skill_parent_id "
        "ON skill(parent_id)"
    ))


MIGRATION = {
    "version": 5,
    "name": "skill_hierarchy_staircase",
    "up": up,
}
