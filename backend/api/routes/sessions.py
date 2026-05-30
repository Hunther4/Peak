import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from typing import Literal
import json
from core.tasks import background_executor
from core.limiter import limiter, get_rate_limit_str

from core.database import get_session, engine
from models.models import Session as PracticeSession, Skill
from core.ai import generate_quick_log_completions
from core.auditor import audit_session
from core.mental import generate_challenge
from models.models import MentalRep, Challenge

logger = logging.getLogger(__name__)

router = APIRouter()

# Threshold constants
ONBOARDING_SESSION_THRESHOLD = 14  # First N sessions per skill are "onboarding" mode
MENTALREP_SESSION_THRESHOLD = 20   # Generate MentalRep after every N sessions

# Validation constants
MIN_DURATION_MINUTES = 10
MIN_PRACTICE_LENGTH = 10

# Quitamos el executor local y el shutdown local

def _process_session_background(session_id: int, skill_id: int, onboarding: bool):
    """
    Corre en un ThreadPoolExecutor separado para NO bloquear el event loop.
    LM Studio puede tardar 10-30 segundos — BackgroundTasks de FastAPI
    bloquea otros requests porque corre en el mismo event loop.
    """
    try:
        with Session(engine) as db:
            practice_session = db.get(PracticeSession, session_id)
            skill = db.get(Skill, skill_id)

            if not practice_session or not skill:
                return

            # 1. Quick Log Completion si aplica
            if practice_session.entry_mode == "quick":
                completions = generate_quick_log_completions(
                    what_i_practiced=practice_session.what_i_practiced,
                    micro_error_found=practice_session.micro_error_found,
                    domain=skill.domain
                )
                practice_session.correction_applied = completions.get("correction_applied", "")
                practice_session.hypothesis_tomorrow = completions.get("hypothesis_tomorrow", "")

            # 2. Auditoría
            audit_result = audit_session(
                session_data={
                    "what_i_practiced": practice_session.what_i_practiced,
                    "difficulty": practice_session.difficulty,
                    "micro_error_found": practice_session.micro_error_found,
                    "correction_applied": practice_session.correction_applied,
                    "hypothesis_tomorrow": practice_session.hypothesis_tomorrow
                },
                domain=skill.domain,
                onboarding_mode=onboarding
            )

            practice_session.was_deliberate = audit_result.was_deliberate
            practice_session.ai_audit_log = audit_result.model_dump_json()
            practice_session.ai_fields_status = "completed"

            # NOTA: El leveling se hace via ASSESSMENTS, no acá.
            # current_level se actualiza cuando se crea un assessment formal.
            # No tocar current_level desde acá.

            db.add(practice_session)
            db.commit()

            # --- Fase 5: Post-session triggers ---
            try:
                # Trigger 1: Challenge si fue deliberada
                if practice_session.was_deliberate is True:
                    _generate_challenge_for_skill(db, practice_session, skill)

                # Trigger 2: MentalRep si corresponde
                _check_mentalrep_triggers(db, practice_session, skill)

            except Exception as trigger_err:
                # Los triggers NUNCA rompen el flujo principal
                logger.warning("Post-session trigger falló para sesión %d: %s", session_id, trigger_err)

    except Exception as e:
        logger.error("Background processing falló para sesión %d: %s", session_id, e)
        # Setear a "failed" para que el usuario sepa que debe reintentar
        try:
            with Session(engine) as db:
                s = db.get(PracticeSession, session_id)
                if s:
                    s.ai_fields_status = "failed"
                    db.add(s)
                    db.commit()
        except Exception as mark_failed_err:
            logger.warning("Error marcando sesión como fallida: %s", mark_failed_err)


def _generate_challenge_for_skill(db: Session, session: PracticeSession, skill: Skill):
    """Genera un challenge después de una sesión deliberada."""
    last_session_str = (
        f"qué: {session.what_i_practiced}, "
        f"dificultad: {session.difficulty}/5, "
        f"error: {session.micro_error_found}"
    )
    result = generate_challenge(
        skill_name=skill.name,
        domain=skill.domain,
        skill_type=skill.skill_type,
        current_level=skill.current_level,
        last_session=last_session_str,
    )
    if result:
        challenge = Challenge(
            skill_id=skill.id,
            description=result.description,
            difficulty_target=result.difficulty_target,
        )
        db.add(challenge)
        db.commit()
        logger.info("Challenge generado para skill '%s' (dif=%d)", skill.name, result.difficulty_target)


def _check_mentalrep_triggers(db: Session, session: PracticeSession, skill: Skill):
    """Verifica si corresponde generar una nueva MentalRep."""
    # Última MentalRep
    last_rep = db.exec(
        select(MentalRep)
        .where(MentalRep.skill_id == skill.id)
        .order_by(MentalRep.created_at.desc())
    ).first()

    # Contar sesiones desde la última MentalRep
    if last_rep:
        sessions_since = db.exec(
            select(PracticeSession)
            .where(
                PracticeSession.skill_id == skill.id,
                PracticeSession.created_at > last_rep.created_at,
            )
        ).all()
        sessions_count = len(sessions_since)
    else:
        sessions_count = db.exec(
            select(PracticeSession).where(PracticeSession.skill_id == skill.id)
        ).all()
        sessions_count = len(sessions_count)

    # Trigger A: MENTALREP_SESSION_THRESHOLD sesiones sin actualizar
    if sessions_count >= MENTALREP_SESSION_THRESHOLD:
        logger.info("MentalRep necesaria: %d sesiones desde la última", sessions_count)
        session.ai_fields_status = "mentalrep_needed"
        db.add(session)
        db.commit()
        return

    # Trigger B: current_level cruza un múltiplo de 10 y no hay rep para este nivel
    if last_rep:
        level_milestone = int(skill.current_level) // 10
        if level_milestone >= 1 and last_rep.version < level_milestone:
            logger.info("MentalRep sugerida: hito de nivel %d alcanzado", level_milestone * 10)
            session.ai_fields_status = "mentalrep_needed"
            db.add(session)
            db.commit()
            return


class SessionCreate(BaseModel):
    skill_id: int
    duration_minutes: int
    what_i_practiced: str = Field(max_length=2000)
    difficulty: int
    micro_error_found: Optional[str] = Field(default=None, max_length=1000)
    correction_applied: Optional[str] = Field(default=None, max_length=2000)
    hypothesis_tomorrow: Optional[str] = Field(default=None, max_length=2000)
    entry_mode: Literal["quick", "full"] = "quick"
    session_data: Optional[dict] = None
    timer_elapsed_sec: Optional[int] = None

    @field_validator("session_data")
    @classmethod
    def validate_session_data(cls, v):
        """Reject session_data that is not a dict or None."""
        if v is not None and not isinstance(v, dict):
            raise ValueError("session_data must be a valid JSON object")
        return v


@router.get("/", response_model=List[PracticeSession])
def get_sessions(
    skill_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_session)
):
    query = select(PracticeSession).order_by(PracticeSession.created_at.desc()).limit(limit)
    if skill_id:
        query = query.where(PracticeSession.skill_id == skill_id)
    return db.exec(query).all()


@router.get("/{session_id}", response_model=PracticeSession)
def get_session_by_id(session_id: int, db: Session = Depends(get_session)):
    session = db.get(PracticeSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return session


@router.post("/", status_code=201)
@limiter.limit(get_rate_limit_str())
def create_session(request: Request, data: SessionCreate, db: Session = Depends(get_session)):
    # Validaciones
    skill = db.get(Skill, data.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill no encontrada")
    if data.duration_minutes < MIN_DURATION_MINUTES:

        raise HTTPException(status_code=400, detail=f"Duración mínima: {MIN_DURATION_MINUTES} minutos")

    if not data.what_i_practiced.strip() or len(data.what_i_practiced.strip()) < MIN_PRACTICE_LENGTH:

        raise HTTPException(status_code=400, detail=f"what_i_practiced debe tener al menos {MIN_PRACTICE_LENGTH} caracteres")
    if data.micro_error_found is not None and not data.micro_error_found.strip():
        raise HTTPException(status_code=400, detail="micro_error_found no puede estar vacío")

    # Validar session_data
    if data.session_data is not None and not isinstance(data.session_data, dict):
        raise HTTPException(status_code=400, detail="Invalid session_data format")

    # Validar modo Full: campos obligatorios
    if data.entry_mode == "full":
        if not data.correction_applied or not data.correction_applied.strip():
            raise HTTPException(status_code=400, detail="Modo full requiere correction_applied")
        if not data.hypothesis_tomorrow or not data.hypothesis_tomorrow.strip():
            raise HTTPException(status_code=400, detail="Modo full requiere hypothesis_tomorrow")

    # Calcular onboarding_mode (primeras N sesiones por skill)
    sessions_count = len(db.exec(
        select(PracticeSession).where(PracticeSession.skill_id == data.skill_id)
    ).all())
    onboarding = sessions_count < ONBOARDING_SESSION_THRESHOLD  # La sesión actual aún no está en DB

    session = PracticeSession(
        skill_id=data.skill_id,
        duration_minutes=data.duration_minutes,
        what_i_practiced=data.what_i_practiced,
        difficulty=data.difficulty,
        micro_error_found=data.micro_error_found,
        correction_applied=data.correction_applied,
        hypothesis_tomorrow=data.hypothesis_tomorrow,
        entry_mode=data.entry_mode,
        timer_elapsed_sec=data.timer_elapsed_sec,
        onboarding_mode=onboarding,
        session_data=json.dumps(data.session_data) if data.session_data else None,
        ai_fields_status="pending"
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    # Lanzar procesamiento IA en ThreadPoolExecutor (NO BackgroundTasks)
    # Esto evita bloquear el event loop mientras LM Studio responde.
    background_executor.submit(_process_session_background, session.id, data.skill_id, onboarding)

    return session


@router.post("/clear-all", status_code=200)
def clear_all_practice_data():
    """Elimina todos los registros de práctica: sesiones, juegos, evaluaciones, etc.
    
    Mantiene skills, perfil de usuario, y configuración. Pensado para el botón
    'Limpiar registros' del frontend.
    """
    from sqlalchemy import text as sa_text
    
    tables_to_clear = [
        "session", "mentalrep", "challenge", "assessment",
        "memorynumbersession", "memorynumberround", "memorynumberattempt",
        "maththinkingsession", "maththinkinground", "maththinkingattempt",
        "iqpracticesession", "iqpracticeround", "iqpracticeattempt",
        "cognitivesession", "cognitivetrial",
    ]
    
    counts = {}
    with engine.connect() as conn:
        for table in tables_to_clear:
            result = conn.execute(sa_text(f"DELETE FROM {table}"))
            counts[table] = result.rowcount
        conn.commit()
    
    logger.info("Datos de práctica limpiados: %s", counts)
    return {"status": "ok", "deleted": counts}


@router.get("/skill/{skill_id}/count")
def get_session_count(skill_id: int, db: Session = Depends(get_session)):
    sessions = db.exec(
        select(PracticeSession).where(PracticeSession.skill_id == skill_id)
    ).all()
    deliberate = [s for s in sessions if s.was_deliberate is True]
    return {
        "total": len(sessions),
        "deliberate": len(deliberate),
        "onboarding_remaining": max(0, ONBOARDING_SESSION_THRESHOLD - len(sessions))
    }
