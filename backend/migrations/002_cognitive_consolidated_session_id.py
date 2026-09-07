"""
Migration 002 — add consolidated_session_id to cognitivesession.

This is an idempotent replay of the column-add that the previous
``_run_migrations`` helper in ``core.database`` performed in-place. Existing
databases that already have the column (because the old helper ran, or
because the column is part of the current SQLModel definition) short-circuit
on the ``PRAGMA table_info`` guard.

The runner is responsible for ordering and recording this migration in
``schema_migrations``; the ``up`` function is a pure schema-mutation step.
"""

from sqlalchemy import text


def up(conn) -> None:
    result = conn.execute(text("PRAGMA table_info(cognitivesession)"))
    columns = [row[1] for row in result]
    if "consolidated_session_id" not in columns:
        conn.execute(
            text(
                "ALTER TABLE cognitivesession "
                "ADD COLUMN consolidated_session_id INTEGER "
                "REFERENCES session(id) ON DELETE SET NULL"
            )
        )


MIGRATION = {
    "version": 2,
    "name": "cognitive_consolidated_session_id",
    "up": up,
}
