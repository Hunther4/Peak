import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel, Field

from core.database import get_session
from models.cognitive_models import CognitiveSkill, CognitiveSession, CognitiveTrial
from models.models import Session as PracticeSession, Skill
from services.cognitive_service import finalizar_session, crear_session
from core.limiter import limiter, get_rate_limit_str

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
    trials: List[CognitiveTrialCreate]


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
    skill = db.get(CognitiveSkill, data.cognitive_skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="CognitiveSkill no encontrada")

    # Enfoque adaptativo: Recuperar el N alcanzado en la última sesión para continuar desde ahí
    last_session = db.exec(
        select(CognitiveSession)
        .where(CognitiveSession.cognitive_skill_id == data.cognitive_skill_id)
        .where(CognitiveSession.fecha_fin != None)
        .order_by(CognitiveSession.fecha_fin.desc())
    ).first()
    
    nivel_inicial = last_session.nivel_n_alcanzado if last_session else 1

    session = CognitiveSession(
        cognitive_skill_id=data.cognitive_skill_id,
        nivel_n_alcanzado=nivel_inicial
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


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
    db: Session = Depends(get_session)
):
    """Consolida una CognitiveSession creando un PracticeSession para la timeline.
    Valida mínimo 10 trials, crea PracticeSession con session_data tipo 'dual_n_back',
    vincula mediante consolidated_session_id y marca is_active=false."""
    cognitive_session = db.get(CognitiveSession, session_id)
    if not cognitive_session:
        raise HTTPException(status_code=404, detail="CognitiveSession no encontrada")

    # Count trials
    trials = db.exec(
        select(CognitiveTrial).where(CognitiveTrial.session_id == session_id)
    ).all()
    if len(trials) < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum 10 trials required before consolidation (found {len(trials)})"
        )

    # Find the standard Dual N-Back skill by skill_type
    skill = db.exec(
        select(Skill).where(Skill.skill_type == "dual_n_back")
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Dual N-Back skill not found — run seed.py first")

    session_data = {
        "type": "dual_n_back",
        "n_level": cognitive_session.nivel_n_alcanzado,
        "accuracy": cognitive_session.tasa_precision,
        "trials_count": len(trials),
        "cognitive_session_id": cognitive_session.id,
    }

    practice_session = PracticeSession(
        skill_id=skill.id,
        what_i_practiced=f"Dual N-Back — N {cognitive_session.nivel_n_alcanzado}, {len(trials)} trials",
        micro_error_found=f"Precisión: {cognitive_session.tasa_precision:.0%}, RT: {cognitive_session.tiempo_reaccion_promedio_ms:.0f}ms",
        difficulty=3,
        entry_mode="quick",
        duration_minutes=max(10, len(trials) * 2),
        session_data=json.dumps(session_data),
    )
    db.add(practice_session)
    db.commit()
    db.refresh(practice_session)

    cognitive_session.consolidated_session_id = practice_session.id
    db.add(cognitive_session)
    db.commit()

    return {
        "status": "consolidated",
        "practice_session_id": practice_session.id,
        "cognitive_session_id": cognitive_session.id,
        "trials_count": len(trials),
        "n_level": cognitive_session.nivel_n_alcanzado,
    }


@router.post("/sessions/{session_id}/finalize/")
def finalize_cognitive_session(
    session_id: int,
    db: Session = Depends(get_session)
):
    """Finaliza la sesión, calcula la tasa de precisión, tiempo de reacción promedio y nuevo nivel N."""
    try:
        result = finalizar_session(db, session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
