"""
Tests de creación de sesiones (T-01 a T-04 del audit).

Validan que la API de sesiones:
- Acepta inputs válidos y retorna ai_fields_status="pending"
- Rechaza inputs que violan las reglas de negocio (duración, modo full, longitud mínima)

NOTA: La IA se mockea en conftest.py — estos tests validan la API, no LM Studio.
"""
import pytest


class TestCreateSession:
    """CRUD de sesiones con validaciones de negocio."""

    # T-01: Sesión válida en modo quick → 200 + ai_fields_status="pending"
    def test_create_session_quick_mode_returns_pending(self, client, skill_factory):
        """Una sesión válida en modo quick retorna 200 con ai_fields_status='pending'."""
        skill = skill_factory()
        response = client.post("/api/sessions/", json={
            "skill_id": skill.id,
            "entry_mode": "quick",
            "what_i_practiced": "Practiqué escalas mayores con metrónomo a 60bpm",
            "micro_error_found": "Dedo meñique se levanta al cambiar de posición",
            "difficulty": 3,
            "duration_minutes": 20,
        })
        # POST create debe retornar 201 (recurso creado), no 200
        assert response.status_code == 201, f"Esperaba 201, obtuve {response.status_code}: {response.text}"
        data = response.json()
        assert data["ai_fields_status"] == "pending"
        assert data["entry_mode"] == "quick"

    # T-02: Duración menor a 10 minutos → 400
    def test_create_session_short_duration_returns_400(self, client, skill_factory):
        """Duración menor a 10 minutos es rechazada con 400."""
        skill = skill_factory()
        response = client.post("/api/sessions/", json={
            "skill_id": skill.id,
            "entry_mode": "quick",
            "what_i_practiced": "Practiqué escalas mayores con metrónomo",
            "micro_error_found": "Dedo meñique se levanta",
            "difficulty": 3,
            "duration_minutes": 5,
        })
        assert response.status_code == 400
        assert "10 minutos" in response.json()["detail"]

    # T-03: Modo full sin correction_applied → 400
    def test_create_session_full_mode_no_correction_returns_400(self, client, skill_factory):
        """En modo full, correction_applied es obligatorio."""
        skill = skill_factory()
        response = client.post("/api/sessions/", json={
            "skill_id": skill.id,
            "entry_mode": "full",
            "what_i_practiced": "Practiqué escalas mayores con metrónomo a 60bpm",
            "micro_error_found": "Dedo meñique se levanta al cambiar de posición",
            "difficulty": 4,
            "duration_minutes": 20,
            # correction_applied intencionalmente omitido
        })
        assert response.status_code == 400
        assert "correction_applied" in response.json()["detail"]

    # T-04: what_i_practiced menor a 10 caracteres → 400
    def test_create_session_short_practiced_returns_400(self, client, skill_factory):
        """what_i_practiced debe tener mínimo 10 caracteres."""
        skill = skill_factory()
        response = client.post("/api/sessions/", json={
            "skill_id": skill.id,
            "entry_mode": "quick",
            "what_i_practiced": "abc",  # Solo 3 chars
            "micro_error_found": "test error with enough detail",
            "difficulty": 3,
            "duration_minutes": 20,
        })
        assert response.status_code == 400
        assert "10 caracteres" in response.json()["detail"]
