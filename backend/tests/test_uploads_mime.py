"""
Tests for MIME whitelist validation on /uploads/ paths (T-03).

Strict TDD: tests written BEFORE production code.
"""
import pytest


class TestUploadsMimeValidation:
    """Integration tests for MIME validation on /uploads/ paths."""

    @pytest.fixture(autouse=True)
    def enable_auth(self, monkeypatch):
        monkeypatch.delenv("DISABLE_AUTH", raising=False)

    def test_uploads_image_png_allowed(self, client, auth_headers):
        """GIVEN /uploads/ path with image/png content-type WHEN request THEN 200 or 404 (not 415)."""
        response = client.get("/uploads/avatars/nonexistent.png", headers=auth_headers)
        # The file doesn't exist but it should NOT be blocked by MIME check
        # (MIME check happens only for upload requests, not GET)
        assert response.status_code != 415

    def test_uploads_get_without_body_not_blocked(self, client, auth_headers):
        """GIVEN GET to /uploads/ without Content-Type WHEN request THEN not 415."""
        response = client.get("/uploads/avatars/nonexistent.png", headers=auth_headers)
        # Static files serve — not a MIME issue
        assert response.status_code in (200, 404)

    def test_uploads_post_with_valid_mime_allowed(self, client, api_key):
        """GIVEN POST to /uploads/ with valid Content-Type WHEN request THEN passes through."""
        # This tests that the middleware doesn't block valid MIME types
        # We use a PUT to /uploads/ path (hypothetical upload endpoint)
        headers = {"X-API-Key": api_key, "Content-Type": "image/png"}
        response = client.put("/uploads/test-file", headers=headers)
        # It may 404 (no such endpoint) but should NOT be blocked by middleware
        assert response.status_code != 415

    def test_uploads_post_with_invalid_mime_returns_415(self, client, auth_headers):
        """GIVEN /uploads/ path with application/x-msdownload WHEN request THEN 415."""
        headers = {
            "X-API-Key": auth_headers["X-API-Key"],
            "Content-Type": "application/x-msdownload",
        }
        response = client.put("/uploads/test-file", headers=headers)
        assert response.status_code == 415

    def test_uploads_post_with_text_plain_allowed(self, client, auth_headers):
        """GIVEN /uploads/ path with text/plain WHEN request THEN passes (not 415)."""
        headers = {
            "X-API-Key": auth_headers["X-API-Key"],
            "Content-Type": "text/plain",
        }
        response = client.put("/uploads/test-file", headers=headers)
        assert response.status_code != 415

    def test_uploads_post_with_application_pdf_allowed(self, client, auth_headers):
        """GIVEN /uploads/ path with application/pdf WHEN request THEN passes (not 415)."""
        headers = {
            "X-API-Key": auth_headers["X-API-Key"],
            "Content-Type": "application/pdf",
        }
        response = client.put("/uploads/test-file", headers=headers)
        assert response.status_code != 415

    def test_non_uploads_path_not_affected(self, client, auth_headers):
        """GIVEN non-/uploads/ path with invalid Content-Type WHEN request THEN not blocked by MIME check."""
        response = client.get(
            "/api/skills/",
            headers={**auth_headers, "Content-Type": "application/x-msdownload"},
        )
        assert response.status_code != 415
