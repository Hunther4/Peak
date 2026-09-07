"""
Tests for the versioned migration system (backend-technical-debt-remediation WU 1)
and the math_thinking import fix (WU 0).

Strict TDD: these tests were written BEFORE the implementation.
The RED phase (failing tests) proves the contract; the GREEN phase
(implementation) makes them pass.
"""

import sys

import pytest
from sqlalchemy import text

# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def clean_schema_migrations_table(engine):
    """The schema_migrations table is NOT in SQLModel.metadata, so the conftest's
    setup_db/teardown does not manage it. Clean it before and after each test
    to keep tests isolated across the StaticPool-backed in-memory engine.
    """
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS schema_migrations"))
    yield
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS schema_migrations"))


FAULTY_MIGRATION_SOURCE = '''\
def up(conn):
    raise RuntimeError("boom: migration failure")

MIGRATION = {
    "version": 999,
    "name": "faulty_test_migration",
    "up": up,
}
'''


@pytest.fixture
def faulty_migration(tmp_path):
    """Inject a faulty migration (version 999, raises RuntimeError) into the
    migrations package's search path so the runner discovers and applies it.
    Restores the original path on teardown.
    """
    import migrations as migrations_pkg

    faulty_file = tmp_path / "999_faulty.py"
    faulty_file.write_text(FAULTY_MIGRATION_SOURCE)

    original_path = list(migrations_pkg.__path__)
    migrations_pkg.__path__.append(str(tmp_path))
    try:
        yield tmp_path
    finally:
        migrations_pkg.__path__[:] = original_path
        sys.modules.pop("migrations.999_faulty", None)


# =============================================================================
# Runner tests — contract for run_migrations(engine)
# =============================================================================


def test_run_migrations_creates_tracking_table(engine):
    """After first run, schema_migrations exists with the three required columns
    (version, name, applied_at) and version is the primary key.
    """
    from migrations.runner import run_migrations

    run_migrations(engine)

    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(schema_migrations)")).fetchall()

    cols = {row[1] for row in rows}
    assert cols == {"version", "name", "applied_at"}

    # version must be the primary key (row[5] is the pk flag in PRAGMA table_info)
    pk_cols = [row[1] for row in rows if row[5]]
    assert "version" in pk_cols


def test_run_migrations_applies_pending(engine):
    """On a fresh DB, both 001 and 002 are recorded in schema_migrations."""
    from migrations.runner import run_migrations

    run_migrations(engine)

    with engine.begin() as conn:
        versions = sorted(
            row[0]
            for row in conn.execute(
                text("SELECT version FROM schema_migrations")
            ).fetchall()
        )

    assert versions == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_run_migrations_is_idempotent(engine):
    """Running twice produces no new rows and no errors."""
    from migrations.runner import run_migrations

    run_migrations(engine)
    run_migrations(engine)  # second call must be a no-op

    with engine.begin() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM schema_migrations")
        ).scalar()

    assert count == 9


def test_migration_002_idempotent_guard(engine):
    """When consolidated_session_id already exists on cognitivesession, migration
    002 short-circuits (no ALTER issued) and is still recorded in schema_migrations.

    Uses a spy on conn.execute to assert the ALTER TABLE statement was NOT called.
    """
    from migrations.runner import run_migrations

    # The conftest's setup_db creates cognitivesession with consolidated_session_id
    # already present (it's in the SQLModel definition). So the guard's PRAGMA
    # check will report the column exists and migration 002 must short-circuit.
    #
    # We spy on conn.execute to capture every statement and assert no ALTER
    # was issued for the consolidated_session_id column.
    executed_statements: list[str] = []
    original_execute = None  # noqa: F841

    from sqlalchemy import event

    @event.listens_for(engine, "before_cursor_execute")
    def capture(conn, cursor, statement, parameters, context, executemany):
        executed_statements.append(statement)

    try:
        run_migrations(engine)  # must not raise
    finally:
        event.remove(engine, "before_cursor_execute", capture)

    # The guard must have prevented the ALTER
    alter_statements = [s for s in executed_statements if "ALTER TABLE cognitivesession" in s]
    assert len(alter_statements) == 0, (
        f"Migration 002's guard should have prevented the ALTER, but got: {alter_statements}"
    )

    # But migration 002 must still be recorded
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT version, name FROM schema_migrations ORDER BY version")
        ).fetchall()

    versions = [r[0] for r in rows]
    assert 2 in versions, f"Expected version 2 in {versions}"
    assert any(r[1] == "cognitive_consolidated_session_id" for r in rows)


def test_run_migrations_applies_in_ascending_order(engine):
    """Migrations are applied in ascending version order, verifiable by the
    version column in schema_migrations.
    """
    from migrations.runner import run_migrations

    run_migrations(engine)

    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT version FROM schema_migrations ORDER BY version")
        ).fetchall()

    versions = [r[0] for r in rows]
    assert versions == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_migration_runner_fails_loud(engine, faulty_migration):
    """A migration that raises propagates the exception out of run_migrations
    (not swallowed as a warning). The failing version must NOT be recorded.
    """
    from migrations.runner import run_migrations

    with pytest.raises(RuntimeError, match="boom: migration failure"):
        run_migrations(engine)

    # The failing version 999 must not be recorded in schema_migrations
    with engine.begin() as conn:
        versions = [
            row[0]
            for row in conn.execute(
                text("SELECT version FROM schema_migrations")
            ).fetchall()
        ]

    assert 999 not in versions, (
        f"Failing migration 999 should not be recorded, got {versions}"
    )


# =============================================================================
# Smoke tests for WU 0 (import fix)
# =============================================================================


def test_math_thinking_import_works():
    """The math_thinking route module imports without ImportError.

    Regression: math_thinking.py used to import `get_db` from core.database,
    but core.database only exports `get_session`. This smoke test fails fast
    if the import is broken again.
    """
    from api.routes import math_thinking  # noqa: F401


def test_main_app_loads():
    """The FastAPI app loads without ImportError.

    main.py imports `from api.routes.math_thinking import router as math_thinking_router`,
    which transitively triggers the broken import. This smoke test catches
    any import-time regression in the route module.
    """
    from main import app  # noqa: F401

    assert app is not None


# =============================================================================
# Validation tests — MIGRATION dict contract enforcement
# =============================================================================


MALFORMED_MIGRATION_SOURCES = {
    "missing_up": '''\
MIGRATION = {
    "version": 50,
    "name": "missing_up",
}
''',
    "string_version": '''\
def up(conn):
    pass

MIGRATION = {
    "version": "50",
    "name": "string_version",
    "up": up,
}
''',
    "non_callable_up": '''\
MIGRATION = {
    "version": 51,
    "name": "non_callable_up",
    "up": "not a function",
}
''',
    "not_a_dict": '''\
MIGRATION = "not a dict"
''',
}


@pytest.mark.parametrize("source_name", list(MALFORMED_MIGRATION_SOURCES.keys()))
def test_malformed_migration_raises_clear_error(engine, tmp_path, source_name):
    """A migration module with a malformed MIGRATION dict must raise a ValueError
    that names the offending module — not a cryptic KeyError or AttributeError.
    """
    from migrations.runner import _discover_migrations

    source = MALFORMED_MIGRATION_SOURCES[source_name]
    # Use a valid filename pattern so it passes the 00N_*.py filter and reaches validation
    faulty_file = tmp_path / "050_test.py"
    faulty_file.write_text(source)

    import migrations as migrations_pkg
    original_path = list(migrations_pkg.__path__)
    migrations_pkg.__path__.append(str(tmp_path))
    try:
        with pytest.raises(ValueError, match="050_test"):
            _discover_migrations()
    finally:
        migrations_pkg.__path__[:] = original_path
        sys.modules.pop("migrations.050_test", None)


def test_duplicate_version_detection(engine, tmp_path):
    """Two migration modules declaring the same version must raise ValueError
    naming the duplicate version, not silently apply both.
    """
    from migrations.runner import _discover_migrations

    dup_a = tmp_path / "100_dup_a.py"
    dup_a.write_text('''\
def up(conn):
    pass
MIGRATION = {"version": 100, "name": "dup_a", "up": up}
''')
    dup_b = tmp_path / "101_dup_b.py"
    dup_b.write_text('''\
def up(conn):
    pass
MIGRATION = {"version": 100, "name": "dup_b", "up": up}
''')

    import migrations as migrations_pkg
    original_path = list(migrations_pkg.__path__)
    migrations_pkg.__path__.append(str(tmp_path))
    try:
        with pytest.raises(ValueError, match="Duplicate migration versions"):
            _discover_migrations()
    finally:
        migrations_pkg.__path__[:] = original_path
        sys.modules.pop("migrations.100_dup_a", None)
        sys.modules.pop("migrations.101_dup_b", None)


def test_earlier_failure_prevents_later_application(engine, tmp_path):
    """A failure in an EARLIER migration must prevent LATER migrations from
    being applied or recorded. Only already-applied earlier migrations remain recorded.
    """
    from migrations.runner import run_migrations

    # Migration 050 succeeds, 051 fails, 052 should never be reached
    mid = tmp_path / "050_good.py"
    mid.write_text('''\
def up(conn):
    pass
MIGRATION = {"version": 50, "name": "good_mid", "up": up}
''')
    bad = tmp_path / "051_bad.py"
    bad.write_text('''\
def up(conn):
    raise RuntimeError("intentional mid-migration failure")
MIGRATION = {"version": 51, "name": "bad_mid", "up": up}
''')
    late = tmp_path / "052_late.py"
    late.write_text('''\
def up(conn):
    pass
MIGRATION = {"version": 52, "name": "late", "up": up}
''')

    import migrations as migrations_pkg
    original_path = list(migrations_pkg.__path__)
    migrations_pkg.__path__.append(str(tmp_path))
    try:
        with pytest.raises(RuntimeError, match="intentional mid-migration failure"):
            run_migrations(engine)
    finally:
        migrations_pkg.__path__[:] = original_path
        for mod_name in ["050_good", "051_bad", "052_late"]:
            sys.modules.pop(f"migrations.{mod_name}", None)

    # 050 was already applied by the first real run; 051 (the failing one)
    # must NOT be recorded; 052 must NOT be recorded (never reached).
    with engine.begin() as conn:
        versions = sorted(
            row[0]
            for row in conn.execute(
                text("SELECT version FROM schema_migrations")
            ).fetchall()
        )

    assert 51 not in versions, f"Failing version 51 should not be recorded, got {versions}"
    assert 52 not in versions, f"Later version 52 should not be reached, got {versions}"
