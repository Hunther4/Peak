import logging
import random
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, func, select

from core.database import get_session
from models.models import ErrorPattern
from models.paes_models import (
    PaesEjeTematico,
    PaesLearningState,
    PaesQuestion,
    PaesQuestionAttempt,
    PaesSocraticStep,
    PaesStudySession,
    PaesSubtopic,
    PaesTopic,
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
    question_count: Optional[int] = None

class SubmitAttemptRequest(BaseModel):
    session_id: str
    question_id: str
    selected_option: str
    time_spent_seconds: int = Field(default=30, ge=1)
    perceived_confidence: int = Field(default=3, ge=1, le=5)
    mistake_cause: Optional[str] = None

class ExamAnswerItem(BaseModel):
    question_id: str
    selected_option: Optional[str] = None
    time_spent_seconds: int = 0

class FinalizeExamRequest(BaseModel):
    answers: List[ExamAnswerItem]

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
    subtopics = session.exec(select(PaesSubtopic).order_by(PaesSubtopic.order_index)).all()
    results = []
    for sub in subtopics:
        topic = session.get(PaesTopic, sub.topic_id) if sub.topic_id else None
        eje = session.get(PaesEjeTematico, topic.eje_id) if (topic and topic.eje_id) else None
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
            "eje_name": eje.name if eje else "General",
            "topic_name": topic.name if topic else "General",
            "mastery": round(state.mastery_score, 2) if (state and state.total_attempts > 0) else 0.0,
            "leitner_box": state.leitner_box if (state and state.total_attempts > 0) else 1,
            "attempts": state.total_attempts if state else 0,
        })
    return {"subtopics": results}

@router.post("/study/session/start")
def start_study_session(req: StartStudySessionRequest, user_id: int = 1, session: Session = Depends(get_session)):
    """Inicia una sesión de estudio o simulacro de examen PAES M1."""
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

    # Selección de preguntas con orden aleatorio
    if req.session_mode == "EXAM":
        count = req.question_count or 65
        all_q = session.exec(
            select(PaesQuestion, PaesEjeTematico.name)
            .join(PaesSubtopic, PaesQuestion.subtopic_id == PaesSubtopic.id)
            .join(PaesTopic, PaesSubtopic.topic_id == PaesTopic.id)
            .join(PaesEjeTematico, PaesTopic.eje_id == PaesEjeTematico.id)
        ).all()

        if not all_q:
            raise HTTPException(status_code=400, detail="No hay preguntas disponibles en el currículum")

        if count >= 65:
            selected_questions = [q for q, _ in all_q]
            random.shuffle(selected_questions)
        elif count <= 15:
            quotas = {"Números": 4, "Álgebra y Funciones": 5, "Geometría": 3, "Probabilidad y Estadística": 3}
            selected_questions = []
            for eje, q_target in quotas.items():
                eje_pool = [q for q, e_name in all_q if e_name == eje]
                random.shuffle(eje_pool)
                selected_questions.extend(eje_pool[:q_target])
            random.shuffle(selected_questions)
        elif count <= 30:
            quotas = {"Números": 7, "Álgebra y Funciones": 10, "Geometría": 7, "Probabilidad y Estadística": 6}
            selected_questions = []
            for eje, q_target in quotas.items():
                eje_pool = [q for q, e_name in all_q if e_name == eje]
                random.shuffle(eje_pool)
                selected_questions.extend(eje_pool[:q_target])
            random.shuffle(selected_questions)
        else:
            all_shuffled = [q for q, _ in all_q]
            random.shuffle(all_shuffled)
            selected_questions = all_shuffled[:count]

        questions = selected_questions
    else:
        q_query = select(PaesQuestion)
        if subtopic:
            q_query = q_query.where(PaesQuestion.subtopic_id == subtopic.id)
        pool = list(session.exec(q_query).all())
        if not pool:
            raise HTTPException(status_code=400, detail="No hay preguntas disponibles para este subtema")
        random.shuffle(pool)
        questions = pool[: (req.question_count or 10)]

    # Mapear preguntas para el frontend (sin revelar la solución correcta)
    frontend_questions = []
    for q in questions:
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

    total_len = len(frontend_questions)
    time_limit = 140 if total_len >= 60 else (65 if total_len >= 30 else 32) if req.session_mode == "EXAM" else None

    return {
        "session_id": session_id,
        "session_mode": req.session_mode,
        "subtopic": subtopic.name if subtopic else "General M1",
        "total_questions": total_len,
        "questions": frontend_questions,
        "time_limit_minutes": time_limit,
    }

@router.post("/study/session/{session_id}/finalize_exam")
def finalize_exam(session_id: str, req: FinalizeExamRequest, user_id: int = 1, session: Session = Depends(get_session)):
    """Consolida un simulacro de examen PAES M1, calcula puntaje DEMRE 100-1000 y desglose por ejes."""
    study_session = session.get(PaesStudySession, session_id)
    if not study_session:
        raise HTTPException(status_code=404, detail="Sesión de examen no encontrada")

    answers_map = {ans.question_id: ans for ans in req.answers}
    question_ids = list(answers_map.keys())
    if not question_ids:
        raise HTTPException(status_code=400, detail="No se recibieron respuestas para evaluar")

    questions = session.exec(select(PaesQuestion).where(PaesQuestion.id.in_(question_ids))).all()

    # Mapear jerarquía de subtemas y ejes
    subtopic_ids = {q.subtopic_id for q in questions}
    subtopics = session.exec(select(PaesSubtopic).where(PaesSubtopic.id.in_(list(subtopic_ids)))).all()
    sub_map = {s.id: s for s in subtopics}

    topic_ids = {s.topic_id for s in subtopics}
    topics = session.exec(select(PaesTopic).where(PaesTopic.id.in_(list(topic_ids)))).all()
    topic_map = {t.id: t for t in topics}

    eje_ids = {t.eje_id for t in topics}
    ejes = session.exec(select(PaesEjeTematico).where(PaesEjeTematico.id.in_(list(eje_ids)))).all()
    eje_map = {e.id: e for e in ejes}

    def get_eje_name(q):
        sub = sub_map.get(q.subtopic_id)
        if not sub:
            return "General"
        top = topic_map.get(sub.topic_id)
        if not top:
            return "General"
        eje = eje_map.get(top.eje_id)
        return eje.name if eje else "General"

    total_items = len(questions)
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    total_time_seconds = 0

    ejes_stats = {
        "Números": {"total": 0, "correct": 0},
        "Álgebra y Funciones": {"total": 0, "correct": 0},
        "Geometría": {"total": 0, "correct": 0},
        "Probabilidad y Estadística": {"total": 0, "correct": 0},
    }

    review_items = []

    for q in questions:
        eje_name = get_eje_name(q)
        if eje_name not in ejes_stats:
            ejes_stats[eje_name] = {"total": 0, "correct": 0}
        ejes_stats[eje_name]["total"] += 1

        ans = answers_map.get(q.id)
        selected_opt = ans.selected_option if ans else None
        time_spent = ans.time_spent_seconds if ans else 0
        total_time_seconds += time_spent

        correct_key = None
        for opt in q.options:
            k = opt.get("id") or opt.get("key")
            if opt.get("is_correct"):
                correct_key = k
                break

        is_correct = False
        if selected_opt:
            if selected_opt == correct_key:
                is_correct = True
                correct_count += 1
                ejes_stats[eje_name]["correct"] += 1
            else:
                incorrect_count += 1
        else:
            unanswered_count += 1

        # Registrar intento en DB para telemetría
        attempt_id = f"paes-att-{uuid.uuid4().hex[:12]}"
        attempt = PaesQuestionAttempt(
            id=attempt_id,
            session_id=study_session.id,
            question_id=q.id,
            user_id=user_id,
            selected_option=selected_opt or "OMITIDA",
            is_correct=is_correct,
            time_spent_seconds=time_spent,
            perceived_confidence=3,
        )
        session.add(attempt)

        review_items.append({
            "question_id": q.id,
            "stem": q.stem,
            "options": q.options,
            "selected_option": selected_opt,
            "correct_option": correct_key,
            "is_correct": is_correct,
            "is_unanswered": not bool(selected_opt),
            "time_spent_seconds": time_spent,
            "difficulty_estimate": q.difficulty_estimate,
            "eje_name": eje_name,
            "subtopic_name": sub_map.get(q.subtopic_id).name if sub_map.get(q.subtopic_id) else "",
            "explanation": q.explanation,
        })

    # Escalar puntaje a 60 aciertos válidos oficiales DEMRE
    scaled_raw = round((correct_count / total_items) * 60) if total_items > 0 else 0
    demre_result = raw_score_to_paes(scaled_raw, total_valid=60)

    study_session.is_completed = True
    study_session.completed_at = datetime.now(timezone.utc)
    study_session.total_items = total_items
    study_session.correct_items = correct_count
    session.add(study_session)
    session.commit()

    ejes_breakdown = []
    for name, stat in ejes_stats.items():
        if stat["total"] > 0:
            pct = round((stat["correct"] / stat["total"]) * 100)
            ejes_breakdown.append({
                "name": name,
                "total": stat["total"],
                "correct": stat["correct"],
                "percentage": pct,
            })

    return {
        "session_id": session_id,
        "total_questions": total_items,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "unanswered_count": unanswered_count,
        "accuracy_pct": round((correct_count / total_items) * 100) if total_items > 0 else 0,
        "total_time_seconds": total_time_seconds,
        "avg_time_per_question": round(total_time_seconds / total_items) if total_items > 0 else 0,
        "scaled_raw_score": scaled_raw,
        "demre": demre_result,
        "ejes_breakdown": ejes_breakdown,
        "review": review_items,
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
