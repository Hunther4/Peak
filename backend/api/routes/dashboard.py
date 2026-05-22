from typing import Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta, timezone

from core.database import get_session
from models.models import Skill, Session as PracticeSession, Assessment

router = APIRouter()


@router.get("/summary")
def get_summary(db: Session = Depends(get_session)):
    skills = db.exec(select(Skill)).all()
    skill_ids = [s.id for s in skills]

    # Batch load: todas las sesiones de todos los skills en 1 query
    all_sessions = db.exec(
        select(PracticeSession)
        .where(PracticeSession.skill_id.in_(skill_ids) if skill_ids else False)
        .order_by(PracticeSession.created_at.desc())
    ).all() if skill_ids else []

    # Batch load: todos los assessments (último por skill)
    all_assessments = db.exec(
        select(Assessment)
        .where(Assessment.skill_id.in_(skill_ids) if skill_ids else False)
        .order_by(Assessment.created_at.desc())
    ).all() if skill_ids else []

    # Indexar por skill_id
    sessions_by_skill = {}
    for s in all_sessions:
        sessions_by_skill.setdefault(s.skill_id, []).append(s)

    last_assessment_by_skill = {}
    for a in all_assessments:
        if a.skill_id not in last_assessment_by_skill:
            last_assessment_by_skill[a.skill_id] = a

    now_utc = datetime.now(timezone.utc)
    week_ago_utc = now_utc - timedelta(days=7)

    summary = []
    for skill in skills:
        sessions = sessions_by_skill.get(skill.id, [])
        last_assessment = last_assessment_by_skill.get(skill.id)

        # Sesiones esta semana (filtrado en Python, pero solo las de este skill)
        sessions_this_week = [s for s in sessions if s.created_at >= week_ago_utc.replace(tzinfo=None)] if sessions else []

        # Racha
        streak = _calculate_streak(sessions, now_utc)

        summary.append({
            "skill": {
                "id": skill.id,
                "name": skill.name,
                "slug": skill.slug,
                "domain": skill.domain,
                "current_level": skill.current_level
            },
            "total_sessions": len(sessions),
            "sessions_this_week": len(sessions_this_week),
            "streak_days": streak,
            "last_assessment": {
                "score": last_assessment.score,
                "type": last_assessment.type,
                "date": last_assessment.created_at.isoformat()
            } if last_assessment else None,
            "last_session": sessions[0].created_at.isoformat() if sessions else None
        })

    return {"skills": summary, "generated_at": now_utc.isoformat()}


@router.get("/timeline")
def get_timeline(
    skill_id: Optional[int] = None,
    limit: int = 30,
    db: Session = Depends(get_session)
):
    # Eager load: trae las sessions con su skill en UNA sola query via JOIN
    query = (
        select(PracticeSession)
        .options(selectinload(PracticeSession.skill))
        .order_by(PracticeSession.created_at.desc())
        .limit(limit)
    )
    if skill_id:
        query = query.where(PracticeSession.skill_id == skill_id)

    sessions = db.exec(query).all()

    timeline = []
    for s in sessions:
        skill = s.skill  # Ya cargado por selectinload — 0 queries extra
        timeline.append({
            "type": "session",
            "id": s.id,
            "skill_name": skill.name if skill else "?",
            "skill_slug": skill.slug if skill else "?",
            "date": s.created_at.isoformat(),
            "duration_minutes": s.duration_minutes,
            "difficulty": s.difficulty,
            "entry_mode": s.entry_mode,
            "was_deliberate": s.was_deliberate,
            "ai_fields_status": s.ai_fields_status,
            "onboarding_mode": s.onboarding_mode,
            "what_i_practiced": s.what_i_practiced,
            "micro_error_found": s.micro_error_found,
            "ai_audit_log": s.ai_audit_log
        })

    return {"timeline": timeline}


def _calculate_streak(sessions: list, now: datetime = None) -> int:
    """
    Calcula la racha de días consecutivos con práctica.
    Incluye hoy Y ayer (racha "en riesgo").
    Usa UTC para evitar problemas de timezone.
    """
    if not sessions:
        return 0

    if now is None:
        now = datetime.now(timezone.utc)

    today = now.date()
    session_dates = set(s.created_at.date() for s in sessions)

    streak = 0
    # Empezar desde hoy; si hoy no hay sesión, intentar desde ayer
    start_date = today if today in session_dates else today - timedelta(days=1)
    check_date = start_date

    while check_date in session_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak
