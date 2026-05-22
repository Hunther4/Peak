import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import Optional
from pydantic import BaseModel, Field

from core.database import get_session
from models.models import Skill
from core.limiter import limiter, get_rate_limit_str

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
def get_skills(db: Session = Depends(get_session)):
    skills = db.exec(select(Skill)).all()
    return skills


@router.get("/{skill_id}")
def get_skill(skill_id: int, db: Session = Depends(get_session)):
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill no encontrada")
    return skill


@router.get("/by-slug/{slug}")
def get_skill_by_slug(slug: str, db: Session = Depends(get_session)):
    skill = db.exec(select(Skill).where(Skill.slug == slug)).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill no encontrada")
    return skill

class SkillCreate(BaseModel):
    name: str = Field(max_length=200)
    domain: str = Field(max_length=200)
    skill_type: str = Field(default="problem_set", max_length=200)
    config_path: str = Field(default="skills/default.yaml", max_length=500)
    slug: str = Field(max_length=200)

@router.post("/", status_code=201)
@limiter.limit(get_rate_limit_str())
def create_skill(request: Request, data: SkillCreate, db: Session = Depends(get_session)):
    existing = db.exec(select(Skill).where(Skill.slug == data.slug)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una skill con ese slug")
    
    new_skill = Skill(
        name=data.name,
        domain=data.domain,
        skill_type=data.skill_type,
        config_path=data.config_path,
        slug=data.slug,
        current_level=1.0
    )
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill
