"""
Tests para api/routes/models.py

Endpoints de status y disponibilidad — probados contra TestClient con DB en memoria.
"""
import pytest
from fastapi.testclient import TestClient


def test_get_models_status(client, auth_headers):
    """GET /api/models/status retorna el modo actual."""
    resp = client.get("/api/models/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "mode" in data
    assert data["mode"] == "local"


def test_get_models_available(client, auth_headers):
    """GET /api/models/available retorna lista de modelos disponibles."""
    resp = client.get("/api/models/available", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
