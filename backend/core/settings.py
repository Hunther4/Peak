from datetime import datetime, timezone

from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlmodel import Session, select

from core.database import engine
from models.models import AppSetting


def get_setting(key: str, default: str = "") -> str:
    """Obtiene un setting de la base de datos (kv_store)."""
    with Session(engine) as session:
        setting = session.exec(select(AppSetting).where(AppSetting.key == key)).first()
        if setting:
            return setting.value
        return default

def set_setting(key: str, value: str) -> None:
    """Guarda o actualiza un setting de manera atómica (UPSERT)."""
    now = datetime.now(timezone.utc)
    stmt = sqlite_insert(AppSetting).values(
        key=key, value=value, updated_at=now
    ).on_conflict_do_update(
        index_elements=[AppSetting.key],
        set_={"value": value, "updated_at": now}
    )
    with Session(engine) as session:
        session.exec(stmt)
        session.commit()

