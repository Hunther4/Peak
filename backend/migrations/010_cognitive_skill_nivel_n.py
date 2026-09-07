"""010 — Add nivel_n_actual to cognitiveskill table.
"""
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

def up(conn):
    """Add nivel_n_actual column to cognitiveskill table if missing."""
    logger.info("Applying migration 010: Adding nivel_n_actual to cognitiveskill")
    res = conn.execute(text("PRAGMA table_info(cognitiveskill)")).fetchall()
    col_names = [r[1] for r in res]
    if "nivel_n_actual" not in col_names:
        conn.execute(text("ALTER TABLE cognitiveskill ADD COLUMN nivel_n_actual INTEGER NOT NULL DEFAULT 1"))

MIGRATION = {
    "version": 10,
    "name": "cognitive_skill_nivel_n",
    "up": up,
}
