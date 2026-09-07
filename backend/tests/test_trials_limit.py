"""
Tests for MAX_TRIALS_PER_REQUEST=500 validator (T-06).

Strict TDD: tests written BEFORE production code.
"""
import pytest


class TestMaxTrialsValidator:
    """Integration tests for the 500-trial limit on bulk upload."""

    def test_trials_under_limit_succeeds(self, client, cog_skill):
        """GIVEN <500 trials WHEN bulk upload THEN succeeds."""
        session_resp = client.post("/api/cognitive/sessions/", json={"cognitive_skill_id": cog_skill.id})
        assert session_resp.status_code == 201
        session_id = session_resp.json()["id"]

        trials = [
            {"estimulo": f"S{i}", "respuesta_esperada": "A", "respuesta_usuario": "A",
             "es_correcto": True, "tiempo_reaccion_ms": 300}
            for i in range(10)
        ]
        resp = client.post("/api/cognitive/trials/", json={"session_id": session_id, "trials": trials})
        assert resp.status_code == 201

    def test_trials_at_limit_succeeds(self, client, cog_skill):
        """GIVEN exactly 500 trials WHEN bulk upload THEN succeeds."""
        session_resp = client.post("/api/cognitive/sessions/", json={"cognitive_skill_id": cog_skill.id})
        assert session_resp.status_code == 201
        session_id = session_resp.json()["id"]

        trials = [
            {"estimulo": f"S{i}", "respuesta_esperada": "A", "respuesta_usuario": "A",
             "es_correcto": True, "tiempo_reaccion_ms": 300}
            for i in range(500)
        ]
        resp = client.post("/api/cognitive/trials/", json={"session_id": session_id, "trials": trials})
        assert resp.status_code == 201

    def test_trials_over_limit_returns_422(self, client, cog_skill):
        """GIVEN 501 trials WHEN bulk upload THEN 422."""
        session_resp = client.post("/api/cognitive/sessions/", json={"cognitive_skill_id": cog_skill.id})
        assert session_resp.status_code == 201
        session_id = session_resp.json()["id"]

        trials = [
            {"estimulo": f"S{i}", "respuesta_esperada": "A", "respuesta_usuario": "A",
             "es_correcto": True, "tiempo_reaccion_ms": 300}
            for i in range(501)
        ]
        resp = client.post("/api/cognitive/trials/", json={"session_id": session_id, "trials": trials})
        assert resp.status_code == 422

    def test_empty_trials_list_rejected(self, client, cog_skill):
        """GIVEN empty trials list WHEN bulk upload THEN 422 (at least 1 required)."""
        session_resp = client.post("/api/cognitive/sessions/", json={"cognitive_skill_id": cog_skill.id})
        assert session_resp.status_code == 201
        session_id = session_resp.json()["id"]

        resp = client.post("/api/cognitive/trials/", json={"session_id": session_id, "trials": []})
        assert resp.status_code == 422


@pytest.fixture
def cog_skill(session):
    """Fixture that creates a CognitiveSkill base."""
    from models.cognitive_models import CognitiveSkill
    skill = CognitiveSkill(
        nombre="Test Skill",
        descripcion="Test",
        fase_iq_base=100
    )
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill
