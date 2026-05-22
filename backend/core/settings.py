from sqlmodel import Session, select
from core.database import engine
from models.models import AppSetting
from datetime import datetime, timezone

def get_setting(key: str, default: str = "") -> str:
    """Obtiene un setting de la base de datos (kv_store)."""
    with Session(engine) as session:
        setting = session.exec(select(AppSetting).where(AppSetting.key == key)).first()
        if setting:
            return setting.value
        return default

def set_setting(key: str, value: str) -> None:
    """Guarda o actualiza un setting en la base de datos."""
    with Session(engine) as session:
        setting = session.exec(select(AppSetting).where(AppSetting.key == key)).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.now(timezone.utc)
        else:
            setting = AppSetting(key=key, value=value)
            session.add(setting)
        session.commit()
