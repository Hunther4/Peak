from typing import List
from sqlmodel import Session as DBSession, select
from datetime import datetime, timezone

from models.cognitive_models import CognitiveTrial, CognitiveSession, CognitiveSkill


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

# Helper functions for DB interaction

def crear_session(db: DBSession, skill_id: int) -> CognitiveSession:
    session = CognitiveSession(cognitive_skill_id=skill_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def agregar_trial(db: DBSession, trial: CognitiveTrial) -> CognitiveTrial:
    db.add(trial)
    db.commit()
    db.refresh(trial)
    return trial

def obtener_trials(db: DBSession, session_id: int) -> List[CognitiveTrial]:
    return db.exec(select(CognitiveTrial).where(CognitiveTrial.session_id == session_id)).all()

def finalizar_session(db: DBSession, session_id: int) -> dict:
    session = db.get(CognitiveSession, session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")
    trials = obtener_trials(db, session_id)
    metrics = procesar_fin_sesion_cognitiva(trials, session.nivel_n_alcanzado)
    # Update session with calculated metrics
    session.tasa_precision = metrics["precision"]
    session.tiempo_reaccion_promedio_ms = metrics["rt_promedio"]
    session.nivel_n_alcanzado = metrics["siguiente_n"]
    session.fecha_fin = datetime.now(timezone.utc)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "session_id": session.id,
        "precision": metrics["precision"],
        "rt_promedio": metrics["rt_promedio"],
        "siguiente_n": metrics["siguiente_n"],
    }
