import logging
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "peak.db"
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


def _run_migrations():
    """Run additive schema migrations for existing databases.
    SQLModel.metadata.create_all only creates missing tables, not missing columns.
    """
    from sqlalchemy import inspect, text
    try:
        with engine.connect() as conn:
            inspector = inspect(conn)
            # Get existing columns for cognitivesession
            columns = [c["name"] for c in inspector.get_columns("cognitivesession")]
            if "consolidated_session_id" not in columns:
                logger.info("Migrating cognitivesession: adding consolidated_session_id column")
                conn.execute(text(
                    "ALTER TABLE cognitivesession ADD COLUMN consolidated_session_id INTEGER REFERENCES session(id) ON DELETE SET NULL"
                ))
                conn.commit()
                logger.info("Migration complete: cognitivesession.consolidated_session_id added")
    except Exception as e:
        logger.warning("Migration skipped (table may not exist yet): %s", e)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _run_migrations()


def get_session():
    with Session(engine) as session:
        yield session
