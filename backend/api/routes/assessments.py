import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import Optional, Literal
from pydantic import BaseModel, Field
import json

from core.database import get_session
from models.models import Assessment, Skill, Session as PracticeSession
from core.limiter import limiter, get_rate_limit_str

logger = logging.getLogger(__name__)

router = APIRouter()


class AssessmentCreate(BaseModel):
    skill_id: int
    type: Literal["probe", "formal"]
    score: float = Field(ge=0.0, le=100.0)
    metrics: Optional[dict] = None
    notes: Optional[str] = Field(default=None, max_length=2000)
    linked_session_id: Optional[int] = None


@router.get("/")
def get_assessments(
    skill_id: Optional[int] = None,
    limit: int = 20,
    db: Session = Depends(get_session)
):
    query = select(Assessment).order_by(Assessment.created_at.desc()).limit(limit)
    if skill_id:
        query = query.where(Assessment.skill_id == skill_id)
    return db.exec(query).all()


@router.get("/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_session)):
    assessment = db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment no encontrado")
    return assessment


@router.post("/", status_code=201)
@limiter.limit(get_rate_limit_str())
def create_assessment(request: Request, data: AssessmentCreate, db: Session = Depends(get_session)):
    skill = db.get(Skill, data.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill no encontrada")

    if data.type not in ("probe", "formal"):
        raise HTTPException(status_code=400, detail="Tipo debe ser 'probe' o 'formal'")

    assessment = Assessment(
        skill_id=data.skill_id,
        type=data.type,
        score=data.score,
        metrics_json=json.dumps(data.metrics) if data.metrics else None,
        notes=data.notes,
        linked_session_id=data.linked_session_id,
    )

    # Si es assessment formal, actualizar current_level de la skill
    if data.type == "formal":
        skill.current_level = data.score

    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment
