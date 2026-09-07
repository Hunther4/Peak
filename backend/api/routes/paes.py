import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, func, select

from core.database import get_session
from models.models import ErrorPattern
from models.paes_models import (
    PaesLearningState,
    PaesQuestion,
    PaesQuestionAttempt,
    PaesSocraticStep,
    PaesStudySession,
    PaesSubtopic,
)
from services.paes.demre_scale import raw_score_to_paes
from services.paes.learning_engine import (
    FSRSState,
    apply_review_capping,
    calculate_retrievability,
    generate_dynamic_study_plan,
    generate_parametric_question,
    search_demre_curriculum,
    update_fsrs_state,
    update_leitner_box,
    update_mastery,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/paes", tags=["PAES M1 Adaptive Study"])

# --- Request / Response Schemas ---

class StartStudySessionRequest(BaseModel):
    session_mode: str = "PRACTICE"  # PRACTICE, LEARN, EXAM, DIAGNOSTIC
    subtopic_slug: Optional[str] = None

class SubmitAttemptRequest(BaseModel):
    session_id: str
    question_id: str
    selected_option: str
    time_spent_seconds: int = Field(default=30, ge=1)
    perceived_confidence: int = Field(default=3, ge=1, le=5)
    mistake_cause: Optional[str] = None

class ParametricRequest(BaseModel):
    template_code: str = "PARAM-M1-ALG-01"
    seed: Optional[int] = None

class SocraticStepRequest(BaseModel):
    session_id: str
    question_id: str
    requested_level: int = Field(default=1, ge=1, le=6)
    student_message: Optional[str] = None

class StudyPlanRequest(BaseModel):
    study_hours_weekly: int = 10
    target_score: int = 750

# --- Endpoints ---

@router.get("/fsrs/status")
def get_fsrs_status(user_id: int = 1, session: Session = Depends(get_session)):
    """Devuelve la retencin proyectada R(t), estabilidad y cola de repasos FSRS."""
    states = session.exec(
        select(PaesLearningState, PaesSubtopic)
        .join(PaesSubtopic, PaesLearningState.subtopic_id == PaesSubtopic.id)
        .where(PaesLearningState.user_id == user_id)
    ).all()

    items = []
    due_items = []
    now = datetime.now(timezone.utc)

    for st, sub in states:
        stab = st.fsrs_stability or 1.0
        diff = st.fsrs_difficulty or 5.0
        elapsed_days = max(0.0, (now - st.last_practiced_at.replace(tzinfo=timezone.utc if st.last_practiced_at.tzinfo is None else None)).total_seconds() / 86400.0)
        retention = calculate_retrievability(elapsed_days, stab)
        is_due = (st.next_review_at.replace(tzinfo=timezone.utc if st.next_review_at.tzinfo is None else None) <= now)

        item_data = {
            "subtopic_id": sub.id,
            "subtopic_name": sub.name,
            "slug": sub.slug,
            "stability": round(stab, 2),
            "difficulty": round(diff, 2),
            "projected_retention": round(retention, 4),
            "mastery_score": round(st.mastery_score, 2),
            "leitner_box": st.leitner_box,
            "total_attempts": st.total_attempts,
            "next_review_at": st.next_review_at.isoformat(),
            "is_due": is_due,
        }
        items.append(item_data)
        if is_due:
            due_items.append(item_data)

    capped_reviews = apply_review_capping(due_items, max_daily_reviews=5)

    return {
        "user_id": user_id,
        "total_subtopics_tracked": len(items),
        "subtopics": items,
        "due_for_review_count": len(due_items),
        "capped_review_queue": capped_reviews,
        "review_capping_limit": 5,
        "timestamp": now.isoformat(),
    }

@router.get("/curriculum/subtopics")
def get_curriculum_subtopics(user_id: int = 1, session: Session = Depends(get_session)):
    """Lista los 13 subtemas oficiales M1 con el estado de dominio del estudiante."""
    subtopics = session.exec(select(PaesSubtopic).order_index(PaesSubtopic.order_index)).all()
    results = []
    for sub in subtopics:
        state = session.exec(
            select(PaesLearningState).where(
                PaesLearningState.user_id == user_id,
                PaesLearningState.subtopic_id == sub.id
            )
        ).first()
        results.append({
            "id": sub.id,
            "name": sub.name,
            "slug": sub.slug,
            "description": sub.description,
            "mastery": round(state.mastery_score, 2) if state else 0.10,
            "leitner_box": state.leitner_box if state else 1,
            "attempts": state.total_attempts if state else 0,
        })
    return {"subtopics": results}

@router.post("/study/session/start")
def start_study_session(req: StartStudySessionRequest, user_id: int = 1, session: Session = Depends(get_session)):
    """Inicia una sesin de estudio PAES seleccionando preguntas va ZDP J(i)."""
    subtopic = None
    if req.subtopic_slug:
        subtopic = session.exec(select(PaesSubtopic).where(PaesSubtopic.slug == req.subtopic_slug)).first()
        if not subtopic:
            raise HTTPException(status_code=404, detail="Subtema no encontrado")

    session_id = f"paes-sess-{uuid.uuid4().hex[:12]}"
    study_session = PaesStudySession(
        id=session_id,
        user_id=user_id,
        session_mode=req.session_mode,
        subtopic_id=subtopic.id if subtopic else None,
        is_completed=False,
    )
    session.add(study_session)

    # Buscar preguntas elegibles
    q_query = select(PaesQuestion)
    if subtopic:
        q_query = q_query.where(PaesQuestion.subtopic_id == subtopic.id)
    questions = session.exec(q_query).all()

    if not questions:
        raise HTTPException(status_code=400, detail="No hay preguntas disponibles para este subtema")

    # Mapear preguntas para el frontend (sin la solucin correcta)
    frontend_questions = []
    for q in questions[:10]: # Bloque de hasta 10 preguntas
        opts = [
            {"key": opt["id"] if "id" in opt else opt.get("key"), "content": opt.get("content", opt.get("text"))}
            for opt in q.options
        ]
        frontend_questions.append({
            "id": q.id,
            "subtopic_id": q.subtopic_id,
            "stem": q.stem,
            "options": opts,
            "difficulty_estimate": q.difficulty_estimate,
            "provenance_type": q.provenance_type,
            "is_pilot": q.is_pilot,
        })

    session.commit()

    return {
        "session_id": session_id,
        "session_mode": req.session_mode,
        "subtopic": subtopic.name if subtopic else "General M1",
        "total_questions": len(frontend_questions),
        "questions": frontend_questions,
    }

@router.post("/study/session/submit")
def submit_attempt(req: SubmitAttemptRequest, user_id: int = 1, session: Session = Depends(get_session)):
    """Evala un intento, actualiza FSRS, calcula fatiga y dispara telemetra cognitiva."""
    study_session = session.get(PaesStudySession, req.session_id)
    if not study_session:
        raise HTTPException(status_code=404, detail="Sesin de estudio no encontrada")

    question = session.get(PaesQuestion, req.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")

    # Determinar si la respuesta es correcta
    is_correct = False
    correct_key = None
    distractor_info = None
    for opt in question.options:
        key = opt.get("id") or opt.get("key")
        if opt.get("is_correct"):
            correct_key = key
        if key == req.selected_option:
            if opt.get("is_correct"):
                is_correct = True
            else:
                distractor_info = opt.get("distractor_type")

    # Registrar intento
    attempt_id = f"paes-att-{uuid.uuid4().hex[:12]}"
    attempt = PaesQuestionAttempt(
        id=attempt_id,
        session_id=study_session.id,
        question_id=question.id,
        user_id=user_id,
        selected_option=req.selected_option,
        is_correct=is_correct,
        time_spent_seconds=req.time_spent_seconds,
        perceived_confidence=req.perceived_confidence,
        mistake_cause=req.mistake_cause or distractor_info,
    )
    session.add(attempt)

    # Actualizar estadsticas de la sesin
    study_session.total_items += 1
    if is_correct:
        study_session.correct_items += 1

    # Actualizar Estado de Aprendizaje FSRS y Leitner
    learning_state = session.exec(
        select(PaesLearningState).where(
            PaesLearningState.user_id == user_id,
            PaesLearningState.subtopic_id == question.subtopic_id
        )
    ).first()

    now = datetime.now(timezone.utc)
    if learning_state:
        fsrs_state = FSRSState(
            stability=learning_state.fsrs_stability or 1.0,
            difficulty=learning_state.fsrs_difficulty or 5.0,
            reps=learning_state.total_attempts,
            lapses=learning_state.total_attempts - learning_state.total_successes,
            last_review_at=learning_state.last_practiced_at,
        )
        new_fsrs, grade = update_fsrs_state(
            fsrs_state,
            is_correct=is_correct,
            confidence=req.perceived_confidence,
            time_spent_seconds=req.time_spent_seconds,
            now=now,
        )

        learning_state.fsrs_stability = new_fsrs.stability
        learning_state.fsrs_difficulty = new_fsrs.difficulty
        learning_state.next_review_at = new_fsrs.next_review_at
        learning_state.total_attempts += 1
        if is_correct:
            learning_state.total_successes += 1
        learning_state.last_practiced_at = now

        leitner_res = update_leitner_box(learning_state.leitner_box, is_correct, now)
        learning_state.leitner_box = leitner_res["box"]
        learning_state.mastery_score = update_mastery(
            learning_state.mastery_score,
            is_correct,
            question.difficulty_estimate,
            req.perceived_confidence,
        )

    # --- BRIDGE COGNITIVO PEAK: Registrar error en telemetra general ---
    if not is_correct:
        error_type = "conceptual"
        if distractor_info in ["CALCULO", "ARITMETICO"]:
            error_type = "aritmtico"
        elif distractor_info in ["TIEMPO", "AZAR"]:
            error_type = "timeout"
        elif distractor_info in ["PROCEDIMENTAL", "LECTURA"]:
            error_type = "descuido"

        try:
            stmt = select(ErrorPattern).where(
                ErrorPattern.skill_id == 1,
                ErrorPattern.error_type == error_type,
            )
            existing_ep = session.exec(stmt).first()
            if existing_ep:
                existing_ep.count += 1
                total_errors = session.exec(
                    select(func.sum(ErrorPattern.count)).where(ErrorPattern.skill_id == 1)
                ).one()
                existing_ep.severity = min(existing_ep.count / max(total_errors or 1, 1), 1.0)
                existing_ep.last_seen = datetime.now(timezone.utc)
                session.add(existing_ep)
            else:
                ep = ErrorPattern(
                    skill_id=1,
                    skill_type="paes_math",
                    error_type=error_type,
                    count=1,
                    severity=0.1,
                )
                session.add(ep)
        except Exception as e:
            logger.warning("No se pudo registrar patron de error cognitivo en Peak: %s", e)

    session.commit()

    return {
        "attempt_id": attempt_id,
        "is_correct": is_correct,
        "correct_option": correct_key,
        "distractor_cause": distractor_info,
        "explanation": question.explanation,
        "fsrs_updated": {
            "stability": round(learning_state.fsrs_stability, 2) if learning_state else None,
            "difficulty": round(learning_state.fsrs_difficulty, 2) if learning_state else None,
            "next_review": learning_state.next_review_at.isoformat() if learning_state else None,
        },
        "session_progress": {
            "total_answered": study_session.total_items,
            "total_correct": study_session.correct_items,
            "accuracy": round(study_session.correct_items / study_session.total_items, 2),
        }
    }

@router.post("/questions/generate_parametric")
def get_parametric_question(req: ParametricRequest):
    """Genera una variante matemtica analtica verificada con SymPy."""
    try:
        data = generate_parametric_question(req.template_code, seed=req.seed)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tutor/step")
def socratic_tutor_step(req: SocraticStepRequest, session: Session = Depends(get_session)):
    """Ofrece pistas socrticas progresivas de nivel 1 a 6 sin revelar la solucin."""
    question = session.get(PaesQuestion, req.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")

    exp = question.explanation
    level_hints = {
        1: exp.get("key_concept", "Analiza cul es el concepto central que relaciona los datos del problema."),
        2: "Recuerda identificar qu valores conoces y qu incgnita necesitas despejar.",
        3: exp.get("frequent_mistake", "Cuidado con los errores de signo o invertir las fracciones."),
        4: "Plantea la ecuacin en una sola variable aislando los trminos lineales a un lado.",
        5: exp.get("short_summary", "Aplica el procedimiento paso a paso simplificando antes de operar."),
        6: exp.get("step_by_step", "Solucin completa: revisa el desglose analtico en la explicacin oficial."),
    }

    hint = level_hints.get(req.requested_level, level_hints[1])

    step = PaesSocraticStep(
        id=f"soc-{uuid.uuid4().hex[:12]}",
        session_id=req.session_id,
        question_id=req.question_id,
        tutor_level=req.requested_level,
        hint_text=hint,
        student_response=req.student_message,
    )
    session.add(step)
    session.commit()

    return {
        "step_id": step.id,
        "tutor_level": req.requested_level,
        "hint": hint,
        "has_more_hints": req.requested_level < 6,
    }

@router.post("/study/plan/generate")
def create_study_plan(req: StudyPlanRequest, user_id: int = 1, session: Session = Depends(get_session)):
    """Genera el cronograma semanal adaptativo segn pesos DEMRE y brecha de puntaje."""
    states = session.exec(
        select(PaesLearningState, PaesSubtopic)
        .join(PaesSubtopic, PaesLearningState.subtopic_id == PaesSubtopic.id)
        .where(PaesLearningState.user_id == user_id)
    ).all()

    subtopic_masteries = {sub.name: st.mastery_score for st, sub in states}
    plan = generate_dynamic_study_plan(
        study_hours_weekly=req.study_hours_weekly,
        target_score=req.target_score,
        subtopic_masteries=subtopic_masteries,
    )
    return plan

@router.get("/rag/search")
def search_curriculum(query: str, top_k: int = 3):
    """Bsqueda semntica en el temario oficial DEMRE M1 2026."""
    results = search_demre_curriculum(query, top_k=top_k)
    return {"query": query, "results": results}

@router.get("/score/convert")
def convert_score(raw_score: int):
    """Convierte un nmero de respuestas correctas (0-60) al puntaje oficial DEMRE (100-1000)."""
    return raw_score_to_paes(raw_score)
