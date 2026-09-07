import logging
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from core.database import get_session
from core.limiter import get_rate_limit_str, limiter
from models.cognitive_models import CognitiveSession, CognitiveSkill, CognitiveTrial
from services.cognitive_service import consolidar_sesion, finalizar_session, iniciar_sesion

logger = logging.getLogger(__name__)

router = APIRouter()


class CognitiveSkillCreate(BaseModel):
    nombre: str = Field(max_length=200)
    descripcion: str = Field(max_length=1000)
    fase_iq_base: int = Field(default=100)


class CognitiveSessionCreate(BaseModel):
    cognitive_skill_id: int


class CognitiveTrialCreate(BaseModel):
    estimulo: str = Field(max_length=200)
    respuesta_esperada: str = Field(max_length=200)
    respuesta_usuario: str = Field(max_length=200)
    es_correcto: bool
    tiempo_reaccion_ms: int = Field(ge=0)


class CognitiveTrialBulkCreate(BaseModel):
    session_id: int
    trials: List[CognitiveTrialCreate] = Field(..., min_length=1, max_length=500)


class ConsolidatePayload(BaseModel):
    elapsed_seconds: Optional[int] = None


@router.get("/skills/", response_model=List[CognitiveSkill])
def get_cognitive_skills(db: Session = Depends(get_session)):
    """Obtiene todas las habilidades cognitivas registradas."""
    return db.exec(select(CognitiveSkill)).all()


@router.post("/skills/", response_model=CognitiveSkill, status_code=201)
@limiter.limit(get_rate_limit_str())
def create_cognitive_skill(
    request: Request,
    data: CognitiveSkillCreate,
    db: Session = Depends(get_session)
):
    """Crea una nueva habilidad cognitiva."""
    existing = db.exec(select(CognitiveSkill).where(CognitiveSkill.nombre == data.nombre)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una habilidad con este nombre")

    new_skill = CognitiveSkill(
        nombre=data.nombre,
        descripcion=data.descripcion,
        fase_iq_base=data.fase_iq_base
    )
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill


@router.post("/sessions/", response_model=CognitiveSession, status_code=201)
@limiter.limit(get_rate_limit_str())
def start_cognitive_session(
    request: Request,
    data: CognitiveSessionCreate,
    db: Session = Depends(get_session)
):
    """Inicia una nueva sesión de entrenamiento cognitivo."""
    try:
        return iniciar_sesion(db, data.cognitive_skill_id)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))


@router.post("/trials/", status_code=201)
def upload_cognitive_trials(
    data: CognitiveTrialBulkCreate,
    db: Session = Depends(get_session)
):
    """Registra un lote (bulk) de trials asociados a una sesión cognitiva."""
    session = db.get(CognitiveSession, data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="CognitiveSession no encontrada")

    if session.fecha_fin is not None:
        raise HTTPException(status_code=400, detail="No se pueden añadir trials a una sesión ya finalizada")

    db_trials = []
    for t in data.trials:
        db_trial = CognitiveTrial(
            session_id=data.session_id,
            estimulo=t.estimulo,
            respuesta_esperada=t.respuesta_esperada,
            respuesta_usuario=t.respuesta_usuario,
            es_correcto=t.es_correcto,
            tiempo_reaccion_ms=t.tiempo_reaccion_ms
        )
        db.add(db_trial)
        db_trials.append(db_trial)

    db.commit()
    return {"status": "success", "count": len(db_trials)}


@router.post("/sessions/{session_id}/consolidate", status_code=201)
def consolidate_cognitive_session(
    session_id: int,
    payload: Optional[ConsolidatePayload] = Body(default=None),
    db: Session = Depends(get_session)
):
    """Consolida una CognitiveSession creando un PracticeSession para la timeline."""
    elapsed_seconds = payload.elapsed_seconds if payload else None
    try:
        return consolidar_sesion(db, session_id, elapsed_seconds)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))


@router.post("/sessions/{session_id}/finalize/")
def finalize_cognitive_session(
    session_id: int,
    payload: Optional[ConsolidatePayload] = Body(default=None),
    db: Session = Depends(get_session)
):
    """Finaliza la sesión, calcula la tasa de precisión, tiempo de reacción promedio y nuevo nivel N.

    Idempotency guard: if the session is already finalized, returns 400.
    This prevents accidental re-computation of the psychometric ladder level.
    """
    session_obj = db.get(CognitiveSession, session_id)
    if not session_obj:
        raise HTTPException(status_code=404, detail=f"CognitiveSession {session_id} no encontrada")

    if session_obj.fecha_fin is not None:
        raise HTTPException(
            status_code=400,
            detail="La sesión ya fue finalizada. No se puede volver a computar el nivel N."
        )

    try:
        result = finalizar_session(db, session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
