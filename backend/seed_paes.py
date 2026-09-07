"""
Seed oficial PAES M1 para Peak.
Puebla el currículum oficial DEMRE M1 2026 y las 65 preguntas verificadas en SQLite.
"""
import json
import logging
import random
from datetime import datetime, timezone

from sqlmodel import Session, select

from core.database import engine
from models.paes_models import (
    PaesCompetency,
    PaesCurriculumVersion,
    PaesEjeTematico,
    PaesLearningState,
    PaesQuestion,
    PaesSubject,
    PaesSubtopic,
    PaesSubtopicPrerequisite,
    PaesTopic,
)
from services.paes.seed_m1 import SEED_DATA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_paes")

def seed_paes_data():
    with Session(engine) as session:
        # 1. Curriculum Version
        cv_data = SEED_DATA["curriculum_version"]
        cv = session.get(PaesCurriculumVersion, cv_data["id"])
        if not cv:
            cv = PaesCurriculumVersion(
                id=cv_data["id"],
                code=cv_data["code"],
                name=cv_data["name"],
                year=cv_data["year"],
                is_active=cv_data["is_active"],
            )
            session.add(cv)
            logger.info("Curriculum Version seeded: %s", cv.code)

        # 2. Subject
        sub_data = SEED_DATA["subject"]
        sub = session.get(PaesSubject, sub_data["id"])
        if not sub:
            sub = PaesSubject(
                id=sub_data["id"],
                curriculum_version_id=sub_data["curriculum_version_id"],
                code=sub_data["code"],
                name=sub_data["name"],
                is_mandatory=sub_data["is_mandatory"],
                total_questions=sub_data["total_questions"],
                scored_questions=sub_data["scored_questions"],
                pilot_questions=sub_data["pilot_questions"],
                duration_minutes=sub_data["duration_minutes"],
            )
            session.add(sub)
            logger.info("Subject seeded: %s", sub.code)

        # 3. Competencies
        for comp in SEED_DATA.get("skills", []):
            c = session.get(PaesCompetency, comp["id"])
            if not c:
                c = PaesCompetency(
                    id=comp["id"],
                    code=comp["code"],
                    name=comp["name"],
                    description=comp.get("description"),
                )
                session.add(c)

        # 4. Ejes Temáticos
        for eje in SEED_DATA.get("ejes", []):
            e = session.get(PaesEjeTematico, eje["id"])
            if not e:
                e = PaesEjeTematico(
                    id=eje["id"],
                    subject_id=eje["subject_id"],
                    name=eje["name"],
                    order_index=eje.get("order_index", 0),
                )
                session.add(e)

        # 5. Topics
        for top in SEED_DATA.get("topics", []):
            t = session.get(PaesTopic, top["id"])
            if not t:
                t = PaesTopic(
                    id=top["id"],
                    eje_id=top["eje_id"],
                    name=top["name"],
                    order_index=top.get("order_index", 0),
                )
                session.add(t)

        # 6. Subtopics
        for subtopic in SEED_DATA.get("subtopics", []):
            st = session.get(PaesSubtopic, subtopic["id"])
            if not st:
                st = PaesSubtopic(
                    id=subtopic["id"],
                    topic_id=subtopic["topic_id"],
                    name=subtopic["name"],
                    slug=subtopic["slug"],
                    description=subtopic.get("description"),
                    order_index=subtopic.get("order_index", 0),
                )
                session.add(st)

        # 7. Prerequisites
        for prereq in SEED_DATA.get("prerequisites", []):
            p = session.get(PaesSubtopicPrerequisite, prereq["id"])
            if not p:
                p = PaesSubtopicPrerequisite(
                    id=prereq["id"],
                    subtopic_id=prereq["subtopic_id"],
                    prerequisite_id=prereq["prerequisite_id"],
                    relationship_type=prereq.get("relationship_type", "STRICT_PREREQUISITE"),
                    minimum_mastery_required=prereq.get("minimum_mastery_required", 0.60),
                )
                session.add(p)

        # 8. Questions (65 items with balanced option keys A, B, C, D)
        for i, q_data in enumerate(SEED_DATA.get("questions", [])):
            raw_options = q_data["options"]
            target_pos = i % 4
            correct_opt = [o for o in raw_options if o.get("is_correct")][0]
            distractors = [o for o in raw_options if not o.get("is_correct")]
            # Deterministic pseudo-random shuffle per question id
            rng = random.Random(q_data["id"])
            rng.shuffle(distractors)

            balanced_opts = []
            d_idx = 0
            for p in range(4):
                if p == target_pos:
                    balanced_opts.append(dict(correct_opt))
                else:
                    balanced_opts.append(dict(distractors[d_idx]))
                    d_idx += 1
            for p, letter in enumerate(["A", "B", "C", "D"]):
                balanced_opts[p]["id"] = letter

            q = session.get(PaesQuestion, q_data["id"])
            if not q:
                q = PaesQuestion(
                    id=q_data["id"],
                    subtopic_id=q_data["subtopic_id"],
                    skill_id=q_data["skill_id"],
                    provenance_type=q_data.get("provenance_type", "ORIGINAL"),
                    stem=q_data["stem"],
                    options_json=json.dumps(balanced_opts, ensure_ascii=False),
                    explanation_json=json.dumps(q_data["explanation"], ensure_ascii=False),
                    difficulty_estimate=q_data.get("difficulty_estimate", 0.5),
                    difficulty_source=q_data.get("difficulty_source", "INITIAL_HEURISTIC"),
                    irt_a=q_data.get("irt_a"),
                    irt_b=q_data.get("irt_b"),
                    irt_c=q_data.get("irt_c"),
                    irt_status=q_data.get("irt_status", "UNINITIALIZED"),
                    is_pilot=bool(q_data.get("is_pilot", False)),
                    source_attribution_json=json.dumps(q_data.get("source_attribution", {}), ensure_ascii=False),
                )
                session.add(q)
            else:
                q.options_json = json.dumps(balanced_opts, ensure_ascii=False)
                session.add(q)

        # 9. Initial student learning states for user 1 (starts at 0% mastery)
        now = datetime.now(timezone.utc)
        for subtopic in SEED_DATA.get("subtopics", []):
            existing_state = session.exec(
                select(PaesLearningState).where(
                    PaesLearningState.user_id == 1,
                    PaesLearningState.subtopic_id == subtopic["id"]
                )
            ).first()
            if not existing_state:
                state_id = f"ls-1-{subtopic['id'][:8]}"
                state = PaesLearningState(
                    id=state_id,
                    user_id=1,
                    subtopic_id=subtopic["id"],
                    mastery_score=0.0,
                    confidence_score=0.0,
                    leitner_box=1,
                    next_review_at=now,
                    fsrs_stability=1.0,
                    fsrs_difficulty=5.0,
                    recent_accuracy=0.0,
                    total_attempts=0,
                    total_successes=0,
                    last_practiced_at=now,
                )
                session.add(state)
            elif existing_state.total_attempts == 0:
                existing_state.mastery_score = 0.0
                existing_state.confidence_score = 0.0
                session.add(existing_state)

        session.commit()
        logger.info("PAES M1 dataset seeded successfully into SQLite (65 items, 13 subtopics).")

if __name__ == "__main__":
    from core.database import create_db_and_tables
    create_db_and_tables()
    seed_paes_data()
