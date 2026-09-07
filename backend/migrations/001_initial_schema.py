"""
Migration 001 — initial schema marker.

This is a no-op baseline. Fresh databases get their tables from
``SQLModel.metadata.create_all`` in ``core.database.create_db_and_tables``,
which runs before the migration runner. This file exists so that the
``schema_migrations`` tracking table starts at version 1 and so that the
runner has at least one discovered module to validate the discovery
mechanism end-to-end.
"""

def up(conn) -> None:
    """No-op baseline migration. Schema is created by SQLModel.metadata.create_all
    before the migration runner is invoked. This migration exists so the
    schema_migrations tracking table starts at version 1.
    """
    return None


MIGRATION = {
    "version": 1,
    "name": "initial_schema",
    "up": up,
}
