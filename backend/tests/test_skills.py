"""
Tests for api/routes/skills.py with auth enabled.

All CRUD scenarios — empty list, get by id, get by slug, create, duplicate slug.
Auth is ON: an autouse fixture overrides conftest's disable_auth so these tests
exercise the full auth+skills path.
"""

import pytest


class TestSkillsWithAuth:
    """Skills CRUD tests with authentication enabled."""

    @pytest.fixture(autouse=True)
    def enable_auth(self, monkeypatch):
        """Override the autouse disable_auth fixture — auth is ON for these tests."""
        monkeypatch.delenv("DISABLE_AUTH", raising=False)

    def test_get_skills_empty(self, client, auth_headers):
        """GET /api/skills/ returns an empty list when no skills exist."""
        resp = client.get("/api/skills/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_skills_with_data(self, client, auth_headers, skill_factory):
        """GET /api/skills/ returns all skills when data exists."""
        skill_factory(slug="skill-a", name="Skill A", domain="memory")
        skill_factory(slug="skill-b", name="Skill B", domain="focus")
        resp = client.get("/api/skills/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_get_skill_by_id_found(self, client, auth_headers, skill_factory):
        """GET /api/skills/{id} returns the skill when it exists."""
        skill = skill_factory(slug="find-by-id", name="Find By ID")
        resp = client.get(f"/api/skills/{skill.id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Find By ID"

    def test_get_skill_by_id_not_found(self, client, auth_headers):
        """GET /api/skills/{id} returns 404 for a non-existent skill."""
        resp = client.get("/api/skills/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_skill_by_slug_found(self, client, auth_headers, skill_factory):
        """GET /api/skills/by-slug/{slug} returns the skill when it exists."""
        skill_factory(slug="my-unique-slug", name="By Slug Match")
        resp = client.get("/api/skills/by-slug/my-unique-slug", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "By Slug Match"

    def test_get_skill_by_slug_not_found(self, client, auth_headers):
        """GET /api/skills/by-slug/{slug} returns 404 for an unknown slug."""
        resp = client.get("/api/skills/by-slug/no-such-slug", headers=auth_headers)
        assert resp.status_code == 404

    def test_create_skill_valid(self, client, auth_headers):
        """POST /api/skills/ creates a new skill with valid data."""
        resp = client.post(
            "/api/skills/",
            headers=auth_headers,
            json={
                "name": "Piano Mastery",
                "domain": "music",
                "skill_type": "staircase",
                "config_path": "skills/piano.yaml",
                "slug": "piano-mastery",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["slug"] == "piano-mastery"
        assert data["name"] == "Piano Mastery"
        assert data["current_level"] == 1.0
        assert data["id"] is not None

    def test_create_skill_duplicate_slug(self, client, auth_headers):
        """POST /api/skills/ returns 400 when slug already exists."""
        payload = {
            "name": "Original",
            "domain": "test",
            "skill_type": "problem_set",
            "config_path": "skills/default.yaml",
            "slug": "duplicate-slug",
        }
        # First create — should succeed
        resp1 = client.post("/api/skills/", headers=auth_headers, json=payload)
        assert resp1.status_code == 201

        # Second create with same slug — should fail
        resp2 = client.post("/api/skills/", headers=auth_headers, json=payload)
        assert resp2.status_code == 400
