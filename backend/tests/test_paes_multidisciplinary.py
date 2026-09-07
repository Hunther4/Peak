import pytest
from fastapi.testclient import TestClient
from main import app
from sqlmodel import Session
from services.paes.demre_scale import raw_score_to_paes, SUBJECT_METADATA
from services.paes.seed_multidisciplinary import seed_multidisciplinary
from services.paes.seed_multidisciplinary_questions import seed_questions
from seed_paes import seed_paes_data

@pytest.fixture
def client(disable_auth):
    return TestClient(app)

@pytest.fixture
def seeded_multidisciplinary(session: Session):
    seed_paes_data()
    seed_multidisciplinary(session)
    seed_questions(session)

def test_demre_scales_all_subjects():
    """Verify that all 5 official PAES subjects produce valid DEMRE 100..1000 conversions."""
    for subject in ["M1", "LECTURA", "M2", "CIENCIAS", "HISTORIA"]:
        meta = SUBJECT_METADATA[subject]
        max_scored = meta["total_scored"]

        # Minimum score
        min_res = raw_score_to_paes(0, total_valid=max_scored, subject_code=subject)
        assert min_res["base_paes_score"] == 100
        assert min_res["subject_code"] == subject

        # Perfect score
        max_res = raw_score_to_paes(max_scored, total_valid=max_scored, subject_code=subject)
        assert max_res["base_paes_score"] == 1000
        assert max_res["subject_code"] == subject

        # Mid score
        mid_res = raw_score_to_paes(max_scored // 2, total_valid=max_scored, subject_code=subject)
        assert 400 <= mid_res["base_paes_score"] <= 850

def test_get_subjects_endpoint(client, seeded_multidisciplinary):
    """GET /api/paes/subjects returns all 5 PAES subjects."""
    resp = client.get("/api/paes/subjects")
    assert resp.status_code == 200
    data = resp.json()
    assert "subjects" in data
    codes = [s["code"] for s in data["subjects"]]
    for expected in ["M1", "LECTURA", "M2", "CIENCIAS", "HISTORIA"]:
        assert expected in codes

def test_get_curriculum_subtopics_filter(client, seeded_multidisciplinary):
    """GET /api/paes/curriculum/subtopics?subject_code=LECTURA filters subtopics."""
    resp = client.get("/api/paes/curriculum/subtopics?subject_code=LECTURA")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["subtopics"]) > 0
    for sub in data["subtopics"]:
        assert sub["subject_code"] == "LECTURA"

def test_start_and_finalize_exam_lectura(client, seeded_multidisciplinary):
    """Start an exam session for LECTURA and finalize with DEMRE conversion."""
    resp_start = client.post("/api/paes/study/session/start", json={
        "session_mode": "EXAM",
        "question_count": 5,
        "subject_code": "LECTURA"
    })
    assert resp_start.status_code == 200
    session_data = resp_start.json()
    assert session_data["subject_code"] == "LECTURA"
    assert len(session_data["questions"]) > 0

    first_q = session_data["questions"][0]
    # Check that stimulus fields exist on question
    assert "stimulus_title" in first_q
    assert "stimulus_text" in first_q

    # Finalize exam
    session_id = session_data["session_id"]
    answers = [{"question_id": q["id"], "selected_option": "A", "time_spent_seconds": 25} for q in session_data["questions"]]
    resp_final = client.post(f"/api/paes/study/session/{session_id}/finalize_exam", json={
        "answers": answers,
        "subject_code": "LECTURA"
    })
    assert resp_final.status_code == 200
    result = resp_final.json()
    assert "demre" in result
    assert result["demre"]["subject_code"] == "LECTURA"
    assert 100 <= result["demre"]["base_paes_score"] <= 1000
    assert "review" in result
    assert len(result["review"]) == len(session_data["questions"])
    assert "stimulus_title" in result["review"][0]
