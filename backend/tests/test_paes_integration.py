from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from main import app
from models.models import Skill
from models.paes_models import (
    PaesLearningState,
    PaesQuestion,
    PaesSubtopic,
)
from services.paes.learning_engine import (
    FSRSState,
    calculate_retrievability,
    generate_parametric_question,
    update_fsrs_state,
)


@pytest.fixture
def client(disable_auth):
    return TestClient(app)

@pytest.fixture
def seeded_paes(session: Session):
    # Ensure baseline skill 1 exists for cognitive telemetry bridge
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

    from models.paes_models import (
        PaesCompetency,
        PaesCurriculumVersion,
        PaesEjeTematico,
        PaesSubject,
        PaesTopic,
    )

    cv = PaesCurriculumVersion(id="cv-01", code="DEMRE-2026", name="Demre 2026", year=2026)
    session.add(cv)
    session.flush()

    sub_subj = PaesSubject(id="subj-01", curriculum_version_id="cv-01", code="M1", name="Matematica 1")
    session.add(sub_subj)
    session.flush()

    eje = PaesEjeTematico(id="eje-01", subject_id="subj-01", name="Algebra")
    session.add(eje)
    session.flush()

    top = PaesTopic(id="top-01", eje_id="eje-01", name="Algebra y Ecuaciones")
    session.add(top)
    session.flush()

    comp = PaesCompetency(id="comp-01", code="RESOLVER_PROBLEMAS", name="Resolver Problemas")
    session.add(comp)
    session.flush()

    # Add dummy subtopic
    sub = PaesSubtopic(
        id="sub-test-01",
        topic_id="top-01",
        name="Ecuaciones Lineales",
        slug="m1-algebra-ecuaciones",
        order_index=1,
    )
    session.add(sub)
    session.flush()

    # Add dummy question
    q = PaesQuestion(
        id="q-test-01",
        subtopic_id="sub-test-01",
        skill_id="comp-01",
        stem="Resuelve 2x + 4 = 10",
        options_json='[{"id": "A", "content": "x = 3", "is_correct": true}, {"id": "B", "content": "x = 2", "is_correct": false, "distractor_type": "CALCULO"}]',
        explanation_json='{"short_summary": "Restar 4 y dividir por 2 da 3", "key_concept": "Despeje de ecuaciones"}',
        difficulty_estimate=0.4,
    )
    session.add(q)
    session.flush()

    # Add learning state
    now = datetime.now(timezone.utc)
    st = PaesLearningState(
        id="ls-test-01",
        user_id=1,
        subtopic_id="sub-test-01",
        mastery_score=0.50,
        fsrs_stability=2.0,
        fsrs_difficulty=4.5,
        last_practiced_at=now,
        next_review_at=now,
    )
    session.add(st)
    session.commit()
    return {"subtopic": sub, "question": q, "state": st}


def test_fsrs_math_engine():
    """Verifica que el motor FSRS calcule la retencin y actualice estabilidad."""
    s = 5.0
    r = calculate_retrievability(elapsed_days=5.0, stability=s)
    assert 0.80 <= r <= 0.95

    initial_state = FSRSState(stability=2.0, difficulty=4.0, reps=1, lapses=0)
    now = datetime.now(timezone.utc)
    updated, grade = update_fsrs_state(
        initial_state,
        is_correct=True,
        confidence=4,
        time_spent_seconds=20,
        now=now,
    )
    assert updated.stability > initial_state.stability
    assert updated.reps == 2


def test_parametric_sympy_generation():
    """Verifica que el generador paramtrico cree preguntas matemticas analticamente vlidas."""
    res = generate_parametric_question("PARAM-M1-ALG-01", seed=42)
    assert "stem" in res
    assert "options" in res
    assert len(res["options"]) == 4
    correct_opts = [opt for opt in res["options"] if opt.get("is_correct")]
    assert len(correct_opts) == 1


def test_paes_fsrs_status_endpoint(client, seeded_paes):
    res = client.get("/api/paes/fsrs/status?user_id=1")
    assert res.status_code == 200
    data = res.json()
    assert "subtopics" in data
    assert len(data["subtopics"]) >= 1
    assert "capped_review_queue" in data


def test_paes_study_session_lifecycle(client, seeded_paes):
    # 1. Iniciar sesin
    start_res = client.post("/api/paes/study/session/start", json={"session_mode": "PRACTICE", "subtopic_slug": "m1-algebra-ecuaciones"})
    assert start_res.status_code == 200
    session_data = start_res.json()
    session_id = session_data["session_id"]
    assert len(session_data["questions"]) >= 1

    # 2. Responder correctamente
    submit_res = client.post("/api/paes/study/session/submit", json={
        "session_id": session_id,
        "question_id": "q-test-01",
        "selected_option": "A",
        "time_spent_seconds": 25,
        "perceived_confidence": 4,
    })
    assert submit_res.status_code == 200
    res_data = submit_res.json()
    assert res_data["is_correct"] is True
    assert res_data["fsrs_updated"]["stability"] is not None

    # 3. Responder errneamente y verificar conexin con telemetra
    submit_err = client.post("/api/paes/study/session/submit", json={
        "session_id": session_id,
        "question_id": "q-test-01",
        "selected_option": "B",
        "time_spent_seconds": 45,
        "perceived_confidence": 2,
    })
    assert submit_err.status_code == 200
    err_data = submit_err.json()
    assert err_data["is_correct"] is False
    assert err_data["distractor_cause"] == "CALCULO"


def test_socratic_tutor_step(client, seeded_paes):
    res = client.post("/api/paes/tutor/step", json={
        "session_id": "sess-test-01",
        "question_id": "q-test-01",
        "requested_level": 1,
    })
    assert res.status_code == 200
    data = res.json()
    assert "hint" in data
    assert data["tutor_level"] == 1
