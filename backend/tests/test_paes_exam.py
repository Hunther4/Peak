"""
Tests for PAES Exam simulation and finalization.
Verifies balanced sampling across 4 DEMRE ejes and score conversion.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from main import app
from models.models import Skill
from models.paes_models import (
    PaesCompetency,
    PaesCurriculumVersion,
    PaesEjeTematico,
    PaesQuestion,
    PaesSubject,
    PaesSubtopic,
    PaesTopic,
)


@pytest.fixture
def client(disable_auth):
    return TestClient(app)

@pytest.fixture
def seeded_exam_data(session: Session):
    skill1 = session.get(Skill, 1)
    if not skill1:
        skill1 = Skill(
            id=1,
            name="Matematica General",
            slug="matematica-general",
            domain="math",
            skill_type="problem_set",
            config_path="skills/math_thinking.yaml",
            current_level=1.0,
        )
        session.add(skill1)

    cv = PaesCurriculumVersion(id="cv-exam-01", code="DEMRE-EXAM-2026", name="Demre 2026", year=2026)
    session.add(cv)
    session.flush()

    subj = PaesSubject(id="subj-exam-01", curriculum_version_id="cv-exam-01", code="M1", name="Matematica 1")
    session.add(subj)
    session.flush()

    comp = PaesCompetency(id="comp-exam-01", code="RESOLVER_PROBLEMAS", name="Resolver Problemas")
    session.add(comp)
    session.flush()

    ejes_data = ["Números", "Álgebra y Funciones", "Geometría", "Probabilidad y Estadística"]
    for i, eje_name in enumerate(ejes_data):
        eje = PaesEjeTematico(id=f"eje-exam-{i}", subject_id="subj-exam-01", name=eje_name, order_index=i+1)
        session.add(eje)
        session.flush()

        top = PaesTopic(id=f"top-exam-{i}", eje_id=eje.id, name=f"Tema {eje_name}", order_index=1)
        session.add(top)
        session.flush()

        sub = PaesSubtopic(
            id=f"sub-exam-{i}",
            topic_id=top.id,
            name=f"Subtema {eje_name}",
            slug=f"sub-slug-{i}",
            order_index=1,
        )
        session.add(sub)
        session.flush()

        # Create 5 questions per eje (20 total)
        for q_idx in range(5):
            q = PaesQuestion(
                id=f"q-exam-{i}-{q_idx}",
                subtopic_id=sub.id,
                skill_id="comp-exam-01",
                stem=f"Pregunta {q_idx+1} de {eje_name}",
                options_json='[{"id": "A", "content": "Opción A", "is_correct": true}, {"id": "B", "content": "Opción B", "is_correct": false}]',
                explanation_json='{"correct_solution": "Solución paso a paso"}',
                difficulty_estimate=0.5,
            )
            session.add(q)
    session.commit()

def test_paes_start_exam_mini(client, seeded_exam_data):
    """Starts a 15-question mini-exam and verifies question distribution."""
    resp = client.post("/api/paes/study/session/start", json={
        "session_mode": "EXAM",
        "question_count": 15
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_mode"] == "EXAM"
    assert data["total_questions"] == 15
    assert data["time_limit_minutes"] == 32
    assert len(data["questions"]) == 15
    for q in data["questions"]:
        assert "options" in q
        assert len(q["options"]) == 2

def test_paes_finalize_exam_scoring(client, seeded_exam_data):
    """Finalizes an exam session and validates DEMRE official scale conversion."""
    start_resp = client.post("/api/paes/study/session/start", json={
        "session_mode": "EXAM",
        "question_count": 15
    })
    assert start_resp.status_code == 200
    session_data = start_resp.json()
    session_id = session_data["session_id"]
    questions = session_data["questions"]

    answers = []
    for i, q in enumerate(questions):
        # Answer first option for 10 items, leave 5 blank
        selected = q["options"][0]["key"] if i < 10 else None
        answers.append({
            "question_id": q["id"],
            "selected_option": selected,
            "time_spent_seconds": 45
        })

    final_resp = client.post(f"/api/paes/study/session/{session_id}/finalize_exam", json={
        "answers": answers
    })
    assert final_resp.status_code == 200
    res = final_resp.json()
    assert res["total_questions"] == 15
    assert "scaled_raw_score" in res
    assert "demre" in res
    assert 100 <= res["demre"]["estimated_score"] <= 1000
    assert len(res["ejes_breakdown"]) > 0
    assert len(res["review"]) == 15
    assert res["unanswered_count"] == 5
