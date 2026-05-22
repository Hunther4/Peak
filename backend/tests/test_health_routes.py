"""
Tests para api/routes/health.py

Endpoint simple de health check.
"""
from fastapi.testclient import TestClient


def test_health_ok(client):
    """GET /api/health retorna status ok."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
