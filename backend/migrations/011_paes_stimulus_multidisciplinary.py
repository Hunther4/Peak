"""011 — Add stimulus_title and stimulus_text to paes_questions table.
"""
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

def up(conn):
    """Add stimulus_title and stimulus_text columns to paes_questions if missing."""
    logger.info("Applying migration 011: Adding stimulus fields to paes_questions")
    res = conn.execute(text("PRAGMA table_info(paes_questions)")).fetchall()
    col_names = [r[1] for r in res]
    if "stimulus_title" not in col_names:
        conn.execute(text("ALTER TABLE paes_questions ADD COLUMN stimulus_title TEXT"))
    if "stimulus_text" not in col_names:
        conn.execute(text("ALTER TABLE paes_questions ADD COLUMN stimulus_text TEXT"))

MIGRATION = {
    "version": 11,
    "name": "paes_stimulus_multidisciplinary",
    "up": up,
}
