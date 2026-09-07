import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from core.database import get_session
from core.limiter import get_rate_limit_str, limiter
from models.models import Skill, SkillLevelHistory
from services.staircase import detect_plateau

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


@router.get("/{skill_id}/sub-skills")
def get_sub_skills(skill_id: int, db: Session = Depends(get_session)):
    """Get direct child skills of a parent skill."""
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill no encontrada")

    sub_skills = db.exec(
        select(Skill).where(Skill.parent_id == skill_id)
    ).all()
    return sub_skills


@router.get("/{skill_id}/level-history")
def get_level_history(
    skill_id: int,
    limit: int = 30,
    db: Session = Depends(get_session),
):
    """Get staircase level history for a skill."""
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill no encontrada")

    history = db.exec(
        select(SkillLevelHistory)
        .where(SkillLevelHistory.skill_id == skill_id)
        .order_by(SkillLevelHistory.created_at.desc())
        .limit(limit)
    ).all()
    return history


@router.get("/{skill_id}/plateau")
def check_plateau(skill_id: int, db: Session = Depends(get_session)):
    """Check if a skill is in a plateau state."""
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill no encontrada")

    return {"is_plateaued": detect_plateau(db, skill_id)}
