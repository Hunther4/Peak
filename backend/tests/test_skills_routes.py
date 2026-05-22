"""
Tests para api/routes/skills.py

Endpoints CRUD de skills — todos probados contra TestClient con DB en memoria.
"""
import pytest
from fastapi.testclient import TestClient


def test_get_skills_empty(client):
    """GET /api/skills/ retorna lista vacía sin skills."""
    resp = client.get("/api/skills/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_and_get_skill(client, skill_factory):
    """POST crea skill, GET la devuelve."""
    skill = skill_factory()
    resp = client.get(f"/api/skills/{skill.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Skill"
    assert data["domain"] == "memory"


def test_get_skill_not_found(client):
    """GET skill inexistente retorna 404."""
    resp = client.get("/api/skills/999")
    assert resp.status_code == 404


def test_get_skill_by_slug(client, skill_factory):
    """GET /by-slug/{slug} encuentra la skill correcta."""
    skill = skill_factory(slug="find-me", name="Find Me", domain="guitar")
    resp = client.get("/api/skills/by-slug/find-me")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Find Me"


def test_get_skill_by_slug_not_found(client):
    """GET /by-slug/{slug} inexistente retorna 404."""
    resp = client.get("/api/skills/by-slug/nonexistent")
    assert resp.status_code == 404


def test_create_skill(client):
    """POST crea skill con valores por defecto."""
    resp = client.post("/api/skills/", json={
        "name": "Piano",
        "domain": "music",
        "skill_type": "staircase",
        "config_path": "skills/piano.yaml",
        "slug": "piano"
    })
    # POST create debe retornar 201 (recurso creado), no 200
    assert resp.status_code == 201, f"Esperaba 201, obtuve {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["slug"] == "piano"
    assert data["current_level"] == 1.0


def test_create_duplicate_slug(client):
    """No se pueden crear dos skills con el mismo slug."""
    payload = {
        "name": "First",
        "domain": "test",
        "skill_type": "problem_set",
        "config_path": "skills/default.yaml",
        "slug": "dup-slug"
    }
    client.post("/api/skills/", json=payload)
    resp = client.post("/api/skills/", json=payload)
    assert resp.status_code == 400


def test_get_all_skills(client, skill_factory):
    """GET /skills/ retorna todas las skills creadas."""
    skill_factory(slug="a", name="A")
    skill_factory(slug="b", name="B")
    resp = client.get("/api/skills/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
