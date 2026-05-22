"""
Tests para api/routes/models.py

Endpoints de model_registry y router — probados contra TestClient con DB en memoria.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


def test_get_models_empty(client):
    """GET /api/models/ retorna lista vacía sin seed."""
    resp = client.get("/api/models/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_models_status(client):
    """GET /api/models/status retorna el modo actual."""
    resp = client.get("/api/models/status")
    assert resp.status_code == 200
    assert "mode" in resp.json()


def test_update_mode(client):
    """PUT /api/models/mode cambia el modo."""
    resp = client.put("/api/models/mode", json={"mode": "api"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    assert resp.json()["mode"] == "api"


def test_update_mode_invalid(client):
    """PUT /api/models/mode con valor inválido retorna 422 (Literal validation)."""
    resp = client.put("/api/models/mode", json={"mode": "nonsense"})
    assert resp.status_code == 422


def test_get_available_for_task_no_filter(client):
    """GET /api/models/available sin task retorna todos."""
    resp = client.get("/api/models/available")
    assert resp.status_code == 200
    # Sin seed retorna lista vacía
    assert resp.json() == []


@patch("api.routes.models.get_best_model_for_task")
def test_get_best_model_task_not_found(mock_best, client):
    """GET /api/models/best sin modelo válido retorna fallback."""
    from models.models import AiModel
    mock_best.return_value = AiModel(
        name="Local (Fallback)",
        provider="lm_studio",
        model_id="local-model",
        capabilities="audit|quick_log|assessment|general",
        score=50
    )
    resp = client.get("/api/models/best?task=unknown")
    assert resp.status_code == 200
    assert resp.json()["provider"] == "lm_studio"
