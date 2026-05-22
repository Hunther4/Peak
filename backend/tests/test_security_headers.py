"""
Tests for SecurityHeadersMiddleware (T-12).

Strict TDD: tests written BEFORE production code.
"""
import pytest


class TestSecurityHeaders:
    """Integration tests for security headers on every response."""

    def test_health_response_has_all_security_headers(self, client):
        """GIVEN a response from any endpoint
        WHEN the response is returned
        THEN all 4 security headers are present with correct values."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "0"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_api_endpoint_has_all_security_headers(self, client):
        """GIVEN a non-health endpoint response
        WHEN the response is returned
        THEN all 4 security headers are still present."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "0"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_404_response_has_security_headers(self, client):
        """GIVEN a 404 response
        WHEN returned
        THEN security headers are still present."""
        response = client.get("/nonexistent-route")
        assert response.status_code == 404
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "0"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
