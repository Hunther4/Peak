"""004 — Create memory session and strategy tracking tables.

Two new tables for Memory Number strategy and performance tracking.
All additive — no existing tables modified.

Tables:
  - memorysessionmeta: strategy metadata per game session
  - memorystrategylog: per-round strategy effectiveness observations
"""

from sqlalchemy import text

TABLES = [
    """CREATE TABLE IF NOT EXISTS memorysessionmeta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_session_id INTEGER NOT NULL REFERENCES memorynumbersession(id) ON DELETE CASCADE,
        strategy_type VARCHAR NOT NULL DEFAULT 'none',
        self_reported_difficulty INTEGER,
        notes TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    "CREATE INDEX IF NOT EXISTS ix_memorysessionmeta_game_session_id ON memorysessionmeta(game_session_id)",
    """CREATE TABLE IF NOT EXISTS memorystrategylog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_session_id INTEGER NOT NULL REFERENCES memorynumbersession(id) ON DELETE CASCADE,
        round_id INTEGER NOT NULL REFERENCES memorynumberround(id) ON DELETE CASCADE,
        strategy_used VARCHAR NOT NULL DEFAULT 'none',
        effective BOOLEAN NOT NULL DEFAULT 0,
        span_at_attempt INTEGER NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    "CREATE INDEX IF NOT EXISTS ix_memorystrategylog_game_session_id ON memorystrategylog(game_session_id)",
    "CREATE INDEX IF NOT EXISTS ix_memorystrategylog_round_id ON memorystrategylog(round_id)",
]


def up(conn):
    """Create the two memory session/strategy tables."""
    for stmt in TABLES:
        conn.execute(text(stmt))


MIGRATION = {
    "version": 4,
    "name": "memory_session_strategy",
    "up": up,
}
