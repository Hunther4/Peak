import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from core.database import engine
from models.models import UserProfile

router = APIRouter()

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "avatars"


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=1, le=150)


class ProfileRead(BaseModel):
    id: int
    name: str
    age: int
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


@router.get("/profile", response_model=ProfileRead | None)
def get_profile():
    """Get the user profile (single-user app — returns first/only profile)."""
    with Session(engine) as db:
        profile = db.exec(select(UserProfile)).first()
        if not profile:
            return None
        return profile


@router.post("/profile", response_model=ProfileRead)
def create_or_update_profile(data: ProfileCreate):
    """Create or update the user profile (upsert — single-user)."""
    with Session(engine) as db:
        existing = db.exec(select(UserProfile)).first()
        if existing:
            existing.name = data.name
            existing.age = data.age
            profile = existing
        else:
            profile = UserProfile(name=data.name, age=data.age)
            db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile


@router.post("/profile/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    ext = Path(file.filename).suffix if file.filename else ".png"
    filename = f"{uuid.uuid4()}{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filepath = UPLOAD_DIR / filename

    content = await file.read()
    filepath.write_bytes(content)

    avatar_url = f"/uploads/avatars/{filename}"
    with Session(engine) as db:
        profile = db.exec(select(UserProfile)).first()
        if profile:
            profile.avatar_url = avatar_url
            db.add(profile)
            db.commit()

    return {"avatar_url": avatar_url}
