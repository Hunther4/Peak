"""
Endpoints de MentalReps y Challenges (Fase 5).
Registrado en main.py como: prefix="/api/mental", tags=["Mental"]
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from core.tasks import background_executor

from core.database import get_session, engine
from models.models import Assessment, Skill, Session as PracticeSession, MentalRep, Challenge
from core.mental import generate_mental_rep, generate_challenge
from core.limiter import limiter, get_rate_limit_str

logger = logging.getLogger(__name__)

router = APIRouter()
# Executor global importado desde core.tasks


# --- Schemas de Request ---

class GenerateMentalRepRequest(BaseModel):
    skill_id: int

class AcceptMentalRepRequest(BaseModel):
    description: str = Field(max_length=2000)
    skill_id: Optional[int] = None

class GenerateChallengeRequest(BaseModel):
    skill_id: int
    difficulty_override: Optional[int] = Field(default=None, ge=1, le=5)

class CompleteChallengeRequest(BaseModel):
    completed: bool = True


# --- MentalRep Endpoints ---

@router.get("/reps")
def get_mental_reps(
    skill_id: Optional[int] = None,
    limit: int = 20,
    db: Session = Depends(get_session),
):
    """Lista representaciones mentales, opcionalmente filtradas por skill."""
    query = select(MentalRep).order_by(MentalRep.created_at.desc()).limit(limit)
    if skill_id:
        query = query.where(MentalRep.skill_id == skill_id)
    return db.exec(query).all()


@router.get("/reps/{rep_id}")
def get_mental_rep(rep_id: int, db: Session = Depends(get_session)):
    """Obtiene una representación mental por ID."""
    rep = db.get(MentalRep, rep_id)
    if not rep:
        raise HTTPException(status_code=404, detail="MentalRep no encontrada")
    return rep


@router.post("/reps/generate")
@limiter.limit(get_rate_limit_str())
def create_mental_rep(request: Request, body: GenerateMentalRepRequest, db: Session = Depends(get_session)):
    """
    Genera una nueva representación mental usando IA.
    Compara con la versión anterior (si existe) y determina si hay un cambio real.
    """
    skill = db.get(Skill, body.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill no encontrada")

    # Obtener última MentalRep
    prev_rep = db.exec(
        select(MentalRep)
        .where(MentalRep.skill_id == body.skill_id)
        .order_by(MentalRep.created_at.desc())
    ).first()

    # Obtener resumen de últimas sesiones
    recent_sessions = db.exec(
        select(PracticeSession)
        .where(PracticeSession.skill_id == body.skill_id)
        .order_by(PracticeSession.created_at.desc())
        .limit(20)
    ).all()

    session_lines = []
    for s in reversed(recent_sessions):
        deliberate = "DELIBERADA" if s.was_deliberate else "no-deliberada"
        session_lines.append(
            f"- [{s.created_at.strftime('%d/%m')}] ({deliberate}) "
            f"dif={s.difficulty}/5, "
            f"qué={s.what_i_practiced[:80]}, "
            f"error={s.micro_error_found[:60] or 'N/A'}"
        )
    session_summary = "\n".join(session_lines) if session_lines else "Sin sesiones registradas."

    result = generate_mental_rep(
        skill_name=skill.name,
        domain=skill.domain,
        skill_type=skill.skill_type,
        current_level=skill.current_level,
        prev_description=prev_rep.description if prev_rep else None,
        prev_version=prev_rep.version if prev_rep else 0,
        session_summary=session_summary,
    )

    if not result:
        return {
            "generated": False,
            "message": "La IA no pudo generar una representación. Verificá que LM Studio esté funcionando.",
            "suggestion": "Intentá de nuevo más tarde o generala manualmente."
        }

    return {
        "generated": True,
        "is_real_shift": result.is_real_shift,
        "description": result.description,
        "reasoning": result.reasoning,
        "key_insight": result.key_insight,
        "prev_version": prev_rep.version if prev_rep else 0,
        "prev_description": prev_rep.description if prev_rep else None,
        "prev_rep_id": prev_rep.id if prev_rep else 0,
    }


@router.post("/reps/{rep_id}/accept", status_code=201)
@limiter.limit(get_rate_limit_str())
def accept_mental_rep(request: Request, rep_id: int, body: AcceptMentalRepRequest, db: Session = Depends(get_session)):
    """
    Acepta (o rechaza) una representación mental generada y la guarda.
    Si el usuario editó la descripción, se guarda la versión editada.
    """
    # Buscar la skill de la rep anterior (si existe).
    # rep_id <= 0 es un valor centinela que indica que no hay una rep anterior
    # (no buscamos en DB), y que se debe crear una nueva rep sin versión previa.
    old_rep = db.get(MentalRep, rep_id) if rep_id > 0 else None

    # Obtener skill_id
    if old_rep:
        skill_id = old_rep.skill_id
        prev_version = old_rep.version
    else:
        if not body.skill_id:
            raise HTTPException(status_code=400, detail="Se requiere skill_id para la primera representación mental.")
        skill_id = body.skill_id
        prev_version = 0

    new_rep = MentalRep(
        skill_id=skill_id,
        description=body.description,
        version=prev_version + 1,
        trigger="insight",
        previous_summary=old_rep.description if old_rep else None,
    )
    db.add(new_rep)
    db.commit()
    db.refresh(new_rep)
    return new_rep


# --- Challenge Endpoints ---

@router.get("/challenges")
def get_challenges(
    skill_id: Optional[int] = None,
    completed: Optional[bool] = None,
    limit: int = 20,
    db: Session = Depends(get_session),
):
    """Lista desafíos, opcionalmente filtrados por skill y estado."""
    query = select(Challenge).order_by(Challenge.created_at.desc()).limit(limit)
    if skill_id:
        query = query.where(Challenge.skill_id == skill_id)
    if completed is not None:
        query = query.where(Challenge.completed == completed)
    return db.exec(query).all()


# --- Auto-suggest next challenge ---
# IMPORTANTE: esta ruta debe definirse ANTES que /challenges/{challenge_id}
# para que FastAPI no interprete "next" como un challenge_id.

@router.get("/challenges/next/{skill_id}")
def get_next_challenge(skill_id: int, db: Session = Depends(get_session)):
    """
    Sugiere cuál debería ser el próximo desafío basado en:
    - Challenges activos (no completados)
    - Último assessment
    - Nivel actual
    """
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill no encontrada")

    # Challenges activos (no completados)
    pending = db.exec(
        select(Challenge)
        .where(Challenge.skill_id == skill_id, Challenge.completed == False)
    ).all()

    # Último assessment
    last_assessment = db.exec(
        select(Assessment)
        .where(Assessment.skill_id == skill_id)
        .order_by(Assessment.created_at.desc())
    ).first()

    return {
        "skill": {"name": skill.name, "level": skill.current_level},
        "pending_challenges": len(pending),
        "next_challenge": pending[0] if pending else None,
        "last_assessment": {
            "score": last_assessment.score,
            "type": last_assessment.type,
            "date": last_assessment.created_at.isoformat()
        } if last_assessment else None,
    }


@router.get("/challenges/{challenge_id}")
def get_challenge(challenge_id: int, db: Session = Depends(get_session)):
    challenge = db.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge no encontrado")
    return challenge


@router.post("/challenges/generate")
@limiter.limit(get_rate_limit_str())
def create_challenge(request: Request, body: GenerateChallengeRequest, db: Session = Depends(get_session)):
    """
    Genera un nuevo desafío usando IA.
    Se basa en la última sesión, nivel actual y RAG de libros.
    """
    skill = db.get(Skill, body.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill no encontrada")

    # Últimas sesiones
    last_sessions = db.exec(
        select(PracticeSession)
        .where(PracticeSession.skill_id == body.skill_id)
        .order_by(PracticeSession.created_at.desc())
        .limit(5)
    ).all()

    if not last_sessions:
        raise HTTPException(
            status_code=400,
            detail="Necesitás al menos una sesión para generar un challenge."
        )

    last = last_sessions[0]
    last_session_str = (
        f"qué: {last.what_i_practiced}, "
        f"dificultad: {last.difficulty}/5, "
        f"error: {last.micro_error_found}, "
        f"corrección: {last.correction_applied or 'N/A'}, "
        f"deliberada: {last.was_deliberate}"
    )

    result = generate_challenge(
        skill_name=skill.name,
        domain=skill.domain,
        skill_type=skill.skill_type,
        current_level=skill.current_level,
        last_session=last_session_str,
        difficulty_override=body.difficulty_override,
    )

    if not result:
        return {
            "generated": False,
            "message": "La IA no pudo generar un desafío. Verificá que LM Studio esté funcionando."
        }

    return {
        "generated": True,
        "description": result.description,
        "difficulty_target": result.difficulty_target,
        "rationale": result.rationale,
    }


@router.patch("/challenges/{challenge_id}/complete")
@limiter.limit(get_rate_limit_str())
def complete_challenge(
    request: Request,
    challenge_id: int,
    body: CompleteChallengeRequest,
    db: Session = Depends(get_session),
):
    """Marca un desafío como completado o pendiente."""
    challenge = db.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge no encontrado")

    challenge.completed = body.completed
    if body.completed:
        challenge.completed_at = datetime.now(timezone.utc)

    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge
