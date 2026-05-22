"""
Tests del dashboard (T-07, T-08).

Validan la función _calculate_streak que es lógica pura.
No requiere API ni DB — se testea directamente.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock


# Importamos la función directamente
from api.routes.dashboard import _calculate_streak


def _create_test_skill(client, slug="test-skill", name="Test Skill", domain="memory"):
    """Helper para crear una skill via API."""
    resp = client.post("/api/skills/", json={
        "name": name,
        "domain": domain,
        "skill_type": "problem_set",
        "config_path": "skills/default.yaml",
        "slug": slug,
    })
    return resp.json()


def _create_test_session(client, skill_id):
    """Helper para crear una sesión via API."""
    resp = client.post("/api/sessions/", json={
        "skill_id": skill_id,
        "entry_mode": "quick",
        "what_i_practiced": "Test practice session with enough detail for validation",
        "micro_error_found": "Error detallado para probar el endpoint",
        "difficulty": 3,
        "duration_minutes": 15,
    })
    return resp.json()


def _make_session(date: datetime) -> MagicMock:
    """Crea un mock de Session con created_at seteado."""
    s = MagicMock()
    s.created_at = date
    return s


class TestCalculateStreak:
    """Lógica de cálculo de racha de práctica."""

    # T-07: 3 días consecutivos → streak=3
    def test_three_consecutive_days_returns_3(self):
        """Tres días seguidos de práctica = racha de 3."""
        now = datetime(2025, 6, 15, 10, 0, tzinfo=timezone.utc)
        sessions = [
            _make_session(datetime(2025, 6, 15, 8, 0)),   # Hoy
            _make_session(datetime(2025, 6, 14, 18, 0)),   # Ayer
            _make_session(datetime(2025, 6, 13, 9, 0)),    # Anteayer
        ]

        assert _calculate_streak(sessions, now) == 3

    # T-08: Gap de 1 día → streak=1
    def test_gap_breaks_streak(self):
        """Un día sin práctica rompe la racha."""
        now = datetime(2025, 6, 15, 10, 0, tzinfo=timezone.utc)
        sessions = [
            _make_session(datetime(2025, 6, 15, 8, 0)),   # Hoy
            # 14 de junio: NADA
            _make_session(datetime(2025, 6, 13, 9, 0)),    # Hace 2 días
            _make_session(datetime(2025, 6, 12, 9, 0)),    # Hace 3 días
        ]

        assert _calculate_streak(sessions, now) == 1

    def test_empty_sessions_returns_0(self):
        """Sin sesiones, la racha es 0."""
        now = datetime(2025, 6, 15, 10, 0, tzinfo=timezone.utc)
        assert _calculate_streak([], now) == 0

    def test_only_yesterday_returns_1(self):
        """Si solo practicaste ayer (no hoy), racha es 1 (en riesgo)."""
        now = datetime(2025, 6, 15, 10, 0, tzinfo=timezone.utc)
        sessions = [
            _make_session(datetime(2025, 6, 14, 18, 0)),   # Ayer
        ]

        assert _calculate_streak(sessions, now) == 1

    def test_multiple_sessions_same_day_count_as_one(self):
        """Tres sesiones el mismo día = 1 día de racha (no 3)."""
        now = datetime(2025, 6, 15, 20, 0, tzinfo=timezone.utc)
        sessions = [
            _make_session(datetime(2025, 6, 15, 8, 0)),
            _make_session(datetime(2025, 6, 15, 12, 0)),
            _make_session(datetime(2025, 6, 15, 17, 0)),
        ]

        assert _calculate_streak(sessions, now) == 1

    def test_long_streak_of_seven_days(self):
        """Racha de 7 días consecutivos."""
        now = datetime(2025, 6, 15, 10, 0, tzinfo=timezone.utc)
        sessions = [
            _make_session(datetime(2025, 6, 15 - i, 9, 0))
            for i in range(7)
        ]

        assert _calculate_streak(sessions, now) == 7


class TestGetTimeline:
    """Tests del endpoint GET /api/dashboard/timeline."""

    def test_timeline_without_skill_id_returns_all_sessions(self, client, skill_factory):
        """GET timeline sin skill_id retorna todas las sesiones."""
        skill1 = skill_factory(slug="skill-a", name="Skill A")
        skill2 = skill_factory(slug="skill-b", name="Skill B")
        _create_test_session(client, skill1.id)
        _create_test_session(client, skill2.id)

        resp = client.get("/api/dashboard/timeline")
        assert resp.status_code == 200
        data = resp.json()
        assert "timeline" in data
        assert len(data["timeline"]) == 2

    def test_timeline_with_skill_id_filters_sessions(self, client, skill_factory):
        """GET timeline con skill_id filtra solo sesiones de ese skill."""
        skill1 = skill_factory(slug="filter-a", name="Filter A")
        skill2 = skill_factory(slug="filter-b", name="Filter B")
        _create_test_session(client, skill1.id)
        _create_test_session(client, skill2.id)
        _create_test_session(client, skill2.id)

        resp = client.get(f"/api/dashboard/timeline?skill_id={skill1.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["timeline"]) == 1

    def test_timeline_empty_returns_empty_list(self, client):
        """Sin sesiones, timeline retorna lista vacía."""
        resp = client.get("/api/dashboard/timeline")
        assert resp.status_code == 200
        data = resp.json()
        assert data["timeline"] == []

    def test_timeline_response_structure(self, client, skill_factory):
        """Cada entrada en timeline tiene los campos esperados."""
        skill = skill_factory(slug="struct-test", name="Struct Test")
        session = _create_test_session(client, skill.id)

        resp = client.get("/api/dashboard/timeline")
        data = resp.json()
        item = data["timeline"][0]

        assert "type" in item
        assert item["type"] == "session"
        assert "id" in item
        assert item["id"] == session["id"]
        assert "skill_name" in item
        assert "date" in item
        assert "duration_minutes" in item
        assert "difficulty" in item
