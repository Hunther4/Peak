"""
Versioned, idempotent, fail-loud database migration system for Peak.

Public API:
    run_migrations(engine) -> None

Discovery:
    The runner scans `backend/migrations/` for modules matching `00N_*.py`
    (excluding itself and any module starting with `_`). Each module must
    expose a module-level `MIGRATION` dict with keys:
        - version: int (positive)
        - name:    str (non-empty)
        - up:      callable(conn) -> None

Ordering:
    Discovered migrations are sorted ascending by `version` and applied in
    that order. The `schema_migrations` tracking table records every
    applied (version, name, applied_at) row.

Error semantics:
    Exceptions raised by a migration's `up` propagate to the caller.
    The runner does not wrap the migration call in a try/except.
    A failure on migration N prevents any migration N+1 from being applied,
    and no row is recorded for the failing version.
"""
import importlib
import logging
import pkgutil
import re
from datetime import datetime, timezone

from sqlalchemy import Engine, text

logger = logging.getLogger(__name__)


MIGRATIONS_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
)
"""

MIGRATION_FILENAME_RE = re.compile(r"^\d{3}_")


def _ensure_tracking_table(conn) -> None:
    conn.execute(text(MIGRATIONS_TABLE_DDL))


def _get_applied_versions(conn) -> set:
    result = conn.execute(text("SELECT version FROM schema_migrations"))
    return {row[0] for row in result}


def _record_migration(conn, version: int, name: str) -> None:
    conn.execute(
        text(
            "INSERT OR IGNORE INTO schema_migrations "
            "(version, name, applied_at) VALUES (:v, :n, :t)"
        ),
        {
            "v": version,
            "n": name,
            "t": datetime.now(timezone.utc).isoformat(),
        },
    )


def _validate_migration(mod_name: str, migration) -> None:
    """Raise ValueError with a clear, module-scoped message if the MIGRATION
    dict is malformed. Contract: dict with version:int(>0), name:str(non-empty),
    up:callable.
    """
    if not isinstance(migration, dict):
        raise ValueError(
            f"{mod_name}: MIGRATION must be a dict, got {type(migration).__name__}"
        )
    if "version" not in migration:
        raise ValueError(f"{mod_name}: MIGRATION missing required key 'version'")
    version = migration["version"]
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise ValueError(
            f"{mod_name}: MIGRATION['version'] must be a positive int, got {version!r}"
        )
    if "name" not in migration:
        raise ValueError(f"{mod_name}: MIGRATION missing required key 'name'")
    name = migration["name"]
    if not isinstance(name, str) or not name:
        raise ValueError(
            f"{mod_name}: MIGRATION['name'] must be a non-empty str, got {name!r}"
        )
    if "up" not in migration:
        raise ValueError(f"{mod_name}: MIGRATION missing required key 'up'")
    if not callable(migration["up"]):
        raise ValueError(
            f"{mod_name}: MIGRATION['up'] must be callable, got {type(migration['up']).__name__}"
        )


def _discover_migrations() -> list:
    """Return MIGRATION dicts from all `00N_*.py` modules in the package,
    sorted ascending by version. Excludes the runner itself and any
    module whose name starts with an underscore. Validates each MIGRATION
    dict and detects duplicate versions; both raise with clear messages.
    """
    import migrations

    discovered = []
    for module_info in pkgutil.iter_modules(migrations.__path__):
        name = module_info.name
        if name.startswith("_") or name == "runner":
            continue
        if not MIGRATION_FILENAME_RE.match(name):
            logger.warning(
                "Module %s in migrations/ does not match 00N_*.py pattern — skipping",
                name,
            )
            continue
        mod = importlib.import_module(f"migrations.{name}")
        migration = getattr(mod, "MIGRATION", None)
        if migration is None:
            logger.warning(
                "Module %s has no MIGRATION dict — skipping", mod.__name__
            )
            continue
        _validate_migration(mod.__name__, migration)
        discovered.append(migration)

    discovered.sort(key=lambda m: m["version"])

    versions = [m["version"] for m in discovered]
    if len(versions) != len(set(versions)):
        from collections import Counter
        dupes = [v for v, c in Counter(versions).items() if c > 1]
        raise ValueError(
            f"Duplicate migration versions detected: {dupes}. "
            f"Each migration must have a unique version number."
        )

    return discovered


def run_migrations(engine: Engine) -> None:
    """Apply all pending migrations in ascending version order. Idempotent.
    Fails loud: any exception from a migration's `up` propagates to the caller.

    Precondition: SQLModel.metadata.create_all(engine) must have been called
    before run_migrations, so that all model-defined tables exist. Migrations
    that reference existing tables (e.g. via PRAGMA table_info) depend on this.
    """
    with engine.begin() as conn:
        _ensure_tracking_table(conn)
        applied = _get_applied_versions(conn)

    for migration in _discover_migrations():
        version = migration["version"]
        name = migration["name"]
        if version in applied:
            logger.info(
                "Migration %03d (%s) already applied — skipping", version, name
            )
            continue
        logger.info("Applying migration %03d (%s)", version, name)
        with engine.begin() as conn:
            migration["up"](conn)
            _record_migration(conn, version, name)
        logger.info("Migration %03d applied successfully", version)
