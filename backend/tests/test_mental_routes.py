"""
Tests para api/routes/mental.py

Endpoints de MentalReps y Challenges — probados contra TestClient con DB en memoria.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from core.mental import MentalRepResult, ChallengeResult


def test_get_reps_empty(client, auth_headers):
    """GET /api/mental/reps retorna lista vacía sin reps."""
    resp = client.get("/api/mental/reps", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_reps_with_data(client, auth_headers, session, skill_factory):
    """GET /api/mental/reps retorna reps cuando existen."""
    from models.models import MentalRep
    from datetime import datetime, timezone

    skill = skill_factory()
    for i in range(3):
        db_rep = MentalRep(
            skill_id=skill.id,
            description=f"Mental rep {i}",
            version=i + 1,
            trigger="insight",
            created_at=datetime.now(timezone.utc),
        )
        session.add(db_rep)
    session.commit()

    resp = client.get("/api/mental/reps", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert data[0]["description"] == "Mental rep 2"


def test_get_challenges_empty(client, auth_headers):
    """GET /api/mental/challenges retorna lista vacía."""
    resp = client.get("/api/mental/challenges", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_challenges_completed_true(client, auth_headers, session, skill_factory):
    """Filtrar challenges por completed=true solo retorna los completados."""
    from models.models import Challenge
    from datetime import datetime, timezone

    skill = skill_factory()
    for i in range(3):
        c = Challenge(
            skill_id=skill.id,
            description=f"Challenge {i}",
            difficulty_target=3,
            completed=(i == 0),  # solo el primero está completado
            created_at=datetime.now(timezone.utc),
        )
        session.add(c)
    session.commit()

    resp = client.get(
        "/api/mental/challenges?completed=true",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["completed"] is True


def test_get_challenges_completed_false(client, auth_headers, session, skill_factory):
    """Filtrar challenges por completed=false retorna los pendientes."""
    from models.models import Challenge
    from datetime import datetime, timezone

    skill = skill_factory()
    for i in range(3):
        c = Challenge(
            skill_id=skill.id,
            description=f"Challenge {i}",
            difficulty_target=3,
            completed=(i == 0),
            created_at=datetime.now(timezone.utc),
        )
        session.add(c)
    session.commit()

    resp = client.get(
        "/api/mental/challenges?completed=false",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(c["completed"] is False for c in data)


def test_get_challenges_no_filter(client, auth_headers, session, skill_factory):
    """Sin filtro completed, retorna todos los challenges."""
    from models.models import Challenge
    from datetime import datetime, timezone

    skill = skill_factory()
    for i in range(3):
        c = Challenge(
            skill_id=skill.id,
            description=f"Challenge {i}",
            difficulty_target=3,
            completed=(i == 0),
            created_at=datetime.now(timezone.utc),
        )
        session.add(c)
    session.commit()

    resp = client.get("/api/mental/challenges", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3


def test_generate_mental_rep_no_skill(client, auth_headers):
    """POST /reps/generate retorna 404 si skill no existe."""
    resp = client.post("/api/mental/reps/generate", json={"skill_id": 999}, headers=auth_headers)
    assert resp.status_code == 404


@patch("api.routes.mental.generate_mental_rep")
def test_generate_mental_rep_success(mock_gen, client, auth_headers, skill_factory):
    """POST /reps/generate retorna resultado generado por IA."""
    skill = skill_factory()
    mock_result = MentalRepResult(
        description="Antes veía X, ahora veo Y",
        is_real_shift=True,
        reasoning="Porque mejoró la comprensión",
        key_insight="Nuevo enfoque"
    )
    mock_gen.return_value = mock_result

    resp = client.post("/api/mental/reps/generate", json={"skill_id": skill.id}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["generated"] is True
    assert "Antes veía X" in data["description"]


@patch("api.routes.mental.generate_mental_rep")
def test_generate_mental_rep_ai_fails(mock_gen, client, auth_headers, skill_factory):
    """POST /reps/generate retorna mensaje cuando la IA falla."""
    skill = skill_factory()
    mock_gen.return_value = None

    resp = client.post("/api/mental/reps/generate", json={"skill_id": skill.id}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["generated"] is False
    assert "LM Studio" in data["message"]


@patch("api.routes.mental.generate_challenge")
def test_generate_challenge_no_sessions(mock_gen, client, auth_headers, skill_factory):
    """POST /challenges/generate retorna 400 sin sesiones."""
    skill = skill_factory()
    resp = client.post("/api/mental/challenges/generate", json={"skill_id": skill.id}, headers=auth_headers)
    assert resp.status_code == 400
    assert "necesitás al menos una sesión" in resp.json()["detail"].lower()


@patch("api.routes.mental.generate_challenge")
def test_generate_challenge_success(mock_gen, client, auth_headers, skill_factory, session_factory):
    """POST /challenges/generate retorna desafío generado."""
    skill = skill_factory()
    session_factory(skill_id=skill.id)
    mock_result = ChallengeResult(
        description="Practica compás 14-16 a 80bpm",
        difficulty_target=3,
        rationale="Para mejorar precisión"
    )
    mock_gen.return_value = mock_result

    resp = client.post("/api/mental/challenges/generate", json={
        "skill_id": skill.id,
        "difficulty_override": 4
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["generated"] is True
    assert data["difficulty_target"] == 3


def test_get_rep_by_id(client, auth_headers, session, skill_factory):
    """GET /reps/{id} retorna la rep si existe."""
    from models.models import MentalRep
    from datetime import datetime, timezone

    skill = skill_factory()
    rep = MentalRep(
        skill_id=skill.id,
        description="Specific rep",
        version=1,
        trigger="insight",
        created_at=datetime.now(timezone.utc),
    )
    session.add(rep)
    session.commit()
    session.refresh(rep)

    resp = client.get(f"/api/mental/reps/{rep.id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["description"] == "Specific rep"


def test_get_rep_not_found(client, auth_headers):
    """GET /reps/{id} inexistente retorna 404."""
    resp = client.get("/api/mental/reps/999", headers=auth_headers)
    assert resp.status_code == 404


def test_get_challenge_by_id(client, auth_headers, session, skill_factory):
    """GET /challenges/{id} retorna el challenge si existe."""
    from models.models import Challenge
    from datetime import datetime, timezone

    skill = skill_factory()
    challenge = Challenge(
        skill_id=skill.id,
        description="Specific challenge",
        difficulty_target=4,
        completed=False,
        created_at=datetime.now(timezone.utc),
    )
    session.add(challenge)
    session.commit()
    session.refresh(challenge)

    resp = client.get(f"/api/mental/challenges/{challenge.id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["description"] == "Specific challenge"


def test_get_challenge_not_found(client, auth_headers):
    """GET /challenges/{id} inexistente retorna 404."""
    resp = client.get("/api/mental/challenges/999", headers=auth_headers)
    assert resp.status_code == 404


def test_complete_challenge_not_found(client, auth_headers):
    """PATCH /challenges/{id}/complete inexistente retorna 404."""
    resp = client.patch("/api/mental/challenges/999/complete", json={"completed": True}, headers=auth_headers)
    assert resp.status_code == 404


def test_complete_challenge_success(client, auth_headers, session, skill_factory):
    """PATCH /challenges/{id}/complete marca un challenge como completado."""
    from models.models import Challenge
    from datetime import datetime, timezone

    skill = skill_factory()
    challenge = Challenge(
        skill_id=skill.id,
        description="Test challenge",
        difficulty_target=3,
        completed=False,
        created_at=datetime.now(timezone.utc),
    )
    session.add(challenge)
    session.commit()
    session.refresh(challenge)

    resp = client.patch(
        f"/api/mental/challenges/{challenge.id}/complete",
        json={"completed": True},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["completed"] is True
    assert data["completed_at"] is not None

    # Confirm persistence
    resp2 = client.get(f"/api/mental/challenges/{challenge.id}", headers=auth_headers)
    assert resp2.json()["completed"] is True


def test_accept_mental_rep_requires_skill_id(client, auth_headers):
    """POST /reps/{id}/accept sin skill_id y sin rep anterior retorna 400."""
    resp = client.post("/api/mental/reps/0/accept", json={
        "description": "Nuevo rep"
    }, headers=auth_headers)
    assert resp.status_code == 400
    assert "skill_id" in resp.json()["detail"]


def test_accept_mental_rep_success_returns_201(client, auth_headers, session, skill_factory):
    """POST /reps/{id}/accept crea una nueva rep y retorna 201."""
    from models.models import MentalRep
    from datetime import datetime, timezone

    skill = skill_factory()
    # First, create an existing rep to have a valid rep_id > 0
    existing = MentalRep(
        skill_id=skill.id,
        description="Existing rep",
        version=1,
        trigger="insight",
        created_at=datetime.now(timezone.utc),
    )
    session.add(existing)
    session.commit()
    session.refresh(existing)

    resp = client.post(
        f"/api/mental/reps/{existing.id}/accept",
        json={"description": "Accepted rep"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["description"] == "Accepted rep"
    assert data["version"] == 2  # incremented from existing.version


def test_next_challenge_no_skill(client, auth_headers):
    """GET /challenges/next/{id} sin skill retorna 404."""
    resp = client.get("/api/mental/challenges/next/999", headers=auth_headers)
    assert resp.status_code == 404


def test_next_challenge_success(client, auth_headers, session, skill_factory):
    """GET /challenges/next/{skill_id} retorna el próximo challenge pendiente."""
    from models.models import Challenge
    from datetime import datetime, timezone

    skill = skill_factory()
    # Create a completed challenge (should be ignored)
    done = Challenge(
        skill_id=skill.id,
        description="Already done",
        difficulty_target=3,
        completed=True,
        created_at=datetime.now(timezone.utc),
    )
    # Create a pending challenge (should be returned)
    pending = Challenge(
        skill_id=skill.id,
        description="Next up",
        difficulty_target=4,
        completed=False,
        created_at=datetime.now(timezone.utc),
    )
    session.add(done)
    session.add(pending)
    session.commit()

    resp = client.get(f"/api/mental/challenges/next/{skill.id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["skill"]["name"] == skill.name
    assert data["pending_challenges"] == 1
    assert data["next_challenge"]["description"] == "Next up"


@patch("api.routes.mental.generate_challenge")
def test_generate_challenge_difficulty_override_too_high(mock_gen, client, auth_headers, skill_factory, session_factory):
    """POST /challenges/generate con difficulty_override > 5 retorna 422."""
    skill = skill_factory()
    session_factory(skill_id=skill.id)
    resp = client.post(
        "/api/mental/challenges/generate",
        json={"skill_id": skill.id, "difficulty_override": 6},
        headers=auth_headers,
    )
    assert resp.status_code == 422


@patch("api.routes.mental.generate_challenge")
def test_generate_challenge_difficulty_override_below_one(mock_gen, client, auth_headers, skill_factory, session_factory):
    """POST /challenges/generate con difficulty_override < 1 retorna 422."""
    skill = skill_factory()
    session_factory(skill_id=skill.id)
    resp = client.post(
        "/api/mental/challenges/generate",
        json={"skill_id": skill.id, "difficulty_override": 0},
        headers=auth_headers,
    )
    assert resp.status_code == 422


@patch("api.routes.mental.generate_challenge")
def test_generate_challenge_ai_fails(mock_gen, client, auth_headers, skill_factory, session_factory):
    """POST /challenges/generate retorna mensaje cuando IA falla."""
    skill = skill_factory()
    session_factory(skill_id=skill.id)
    mock_gen.return_value = None

    resp = client.post("/api/mental/challenges/generate", json={"skill_id": skill.id}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["generated"] is False
