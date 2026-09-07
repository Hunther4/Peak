import json
from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Session as DBSession
from sqlmodel import select

from models.cognitive_models import CognitiveSession, CognitiveSkill, CognitiveTrial
from models.models import Session as PracticeSession
from models.models import Skill


def calcular_escalera_psicometrica(tasa_precision: float, nivel_n_actual: int) -> int:
    """Algoritmo estándar de adaptación para entrenamiento de memoria de trabajo (Dual N-Back).
    - Precisión >= 0.80 → aumenta nivel (N+1)
    - Precisión < 0.70 → disminuye nivel (N-1) (mínimo 1)
    - Entre 0.70 y 0.79 → mantiene nivel
    """
    if tasa_precision >= 0.80:
        return nivel_n_actual + 1
    elif tasa_precision < 0.70 and nivel_n_actual > 1:
        return nivel_n_actual - 1
    return nivel_n_actual


def procesar_fin_sesion_cognitiva(trials: List[CognitiveTrial], nivel_n_actual: int) -> dict:
    """Calcula métricas a partir de los trials y determina el siguiente nivel N.
    Devuelve un dict con precisión, tiempo de reacción promedio y próximo nivel.
    """
    if not trials:
        return {"precision": 0.0, "rt_promedio": 0.0, "siguiente_n": nivel_n_actual}

    correctos = sum(1 for t in trials if t.es_correcto)
    tasa_precision = correctos / len(trials)
    total_rt = sum(t.tiempo_reaccion_ms for t in trials)
    rt_promedio = total_rt / len(trials)
    siguiente_n = calcular_escalera_psicometrica(tasa_precision, nivel_n_actual)
    return {
        "precision": round(tasa_precision, 2),
        "rt_promedio": round(rt_promedio, 2),
        "siguiente_n": siguiente_n,
    }


def iniciar_sesion(db: DBSession, skill_id: int) -> CognitiveSession:
    # Fetch skill
    skill = db.get(CognitiveSkill, skill_id)
    if not skill:
        raise ValueError("CognitiveSkill not found")

    # Find last session to determine initial N level
    last_session = db.exec(
        select(CognitiveSession)
        .where(CognitiveSession.cognitive_skill_id == skill_id)
        .where(CognitiveSession.fecha_fin != None)  # noqa: E711
        .order_by(CognitiveSession.fecha_fin.desc())
    ).first()

    nivel_inicial = (
        last_session.nivel_n_alcanzado
        if last_session and last_session.nivel_n_alcanzado
        else getattr(skill, "nivel_n_actual", 1)
    )

    # Create session
    session = CognitiveSession(
        cognitive_skill_id=skill_id,
        nivel_n_alcanzado=nivel_inicial
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def consolidar_sesion(db: DBSession, session_id: int, elapsed_seconds: Optional[int]) -> dict:
    # Fetch cognitive session
    cognitive_session = db.get(CognitiveSession, session_id)
    if not cognitive_session:
        raise ValueError("CognitiveSession not found")

    # Guard: require finalized session so accuracy/RT metrics are populated
    if cognitive_session.fecha_fin is None:
        raise ValueError("Cognitive session is not finalized — call finalizar_session first")

    # Count trials
    trials = obtener_trials(db, session_id)
    if len(trials) < 10:
        raise ValueError(f"Minimum 10 trials required before consolidation (found {len(trials)})")

    # Fetch Dual N-Back skill
    skill = db.exec(
        select(Skill).where(Skill.skill_type == "dual_n_back")
    ).first()
    if not skill:
        raise ValueError("Dual N-Back skill not found — run seed.py first")

    session_data = {
        "type": "dual_n_back",
        "n_level": cognitive_session.nivel_n_alcanzado,
        "accuracy": cognitive_session.tasa_precision,
        "trials_count": len(trials),
        "cognitive_session_id": cognitive_session.id,
    }
    if elapsed_seconds is not None:
        session_data["elapsed_seconds"] = elapsed_seconds

    # Realistic duration calculation: use elapsed_seconds if available, else ~3s per trial
    if elapsed_seconds is not None:
        duration_minutes = max(1, round(elapsed_seconds / 60))
    else:
        duration_minutes = max(10, round(len(trials) * 3 / 60))

    practice_session = PracticeSession(
        skill_id=skill.id,
        what_i_practiced=f"Dual N-Back — N {cognitive_session.nivel_n_alcanzado}, {len(trials)} trials",
        micro_error_found=f"Precisión: {cognitive_session.tasa_precision:.0%}, RT: {cognitive_session.tiempo_reaccion_promedio_ms:.0f}ms",
        difficulty=min(5, max(1, cognitive_session.nivel_n_alcanzado)),
        entry_mode="quick",
        duration_minutes=duration_minutes,
        session_data=json.dumps(session_data),
    )
    db.add(practice_session)
    # Flush to get practice_session.id before linking
    db.flush()

    # Link both in a single atomic transaction
    cognitive_session.consolidated_session_id = practice_session.id
    db.add(cognitive_session)
    db.commit()
    db.refresh(practice_session)
    db.refresh(cognitive_session)

    # --- Adaptive staircase (Ericsson 1↑/1↓) ---
    from services.staircase import apply_staircase, compute_practice_level, determine_session_success

    session_success = determine_session_success(db, cognitive_session, skill=skill)
    if skill:
        apply_staircase(db, skill, session_success,
                        trigger="session_consolidation",
                        session_id=practice_session.id)
        skill.practice_level = compute_practice_level(practice_session)
        skill.current_level = float(cognitive_session.nivel_n_alcanzado)
        db.add(skill)
        db.commit()

    return {
        "status": "consolidated",
        "practice_session_id": practice_session.id,
        "cognitive_session_id": cognitive_session.id,
        "trials_count": len(trials),
        "n_level": cognitive_session.nivel_n_alcanzado,
        "summary": {
            "rounds_completed": len(trials),
            "n_level": cognitive_session.nivel_n_alcanzado,
            "accuracy": cognitive_session.tasa_precision,
            "cognitive_session_id": cognitive_session.id,
        },
    }


def obtener_trials(db: DBSession, session_id: int) -> List[CognitiveTrial]:
    return db.exec(select(CognitiveTrial).where(CognitiveTrial.session_id == session_id)).all()

def finalizar_session(db: DBSession, session_id: int) -> dict:
    session = db.get(CognitiveSession, session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")
    trials = obtener_trials(db, session_id)
    metrics = procesar_fin_sesion_cognitiva(trials, session.nivel_n_alcanzado)
    # Update session with calculated metrics AND new N level
    session.tasa_precision = metrics["precision"]
    session.tiempo_reaccion_promedio_ms = metrics["rt_promedio"]
    session.nivel_n_alcanzado = metrics["siguiente_n"]
    session.fecha_fin = datetime.now(timezone.utc)
    db.add(session)

    # Persist updated N level to CognitiveSkill
    cog_skill = db.get(CognitiveSkill, session.cognitive_skill_id)
    if cog_skill:
        cog_skill.nivel_n_actual = metrics["siguiente_n"]
        db.add(cog_skill)

    db.commit()
    db.refresh(session)
    return {
        "session_id": session.id,
        "precision": metrics["precision"],
        "rt_promedio": metrics["rt_promedio"],
        "siguiente_n": metrics["siguiente_n"],
    }
