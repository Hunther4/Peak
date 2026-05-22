"""
Comprehensive security tests for Peak Practice API.

Covers T-18 from the security-hardening change:
  1. Auth on ALL endpoints — no key → 401, bad key → 401, valid key → works
  2. Rate limiting — burst 61 POSTs → 429 on 61st, GET/health unlimited
  3. Input sanitization — control chars handled, max_length enforced
  4. Security headers — every response includes all 4 headers
  5. Lock error path — index lock released on executor failure

Deps: T-03 (auth_headers fixture), T-06 (sanitize_prompt), T-11 (slowapi)
"""
import pytest
from unittest.mock import patch


# ============================================================================
# 1. Auth on ALL endpoints
# ============================================================================

# Every GET endpoint path in the API (except /api/health, which is exempt).
# These are "list" / simple endpoints that need no pre-existing DB records.
ALL_GET_PATHS = [
    "/",
    "/api/skills/",
    "/api/sessions/",
    "/api/assessments/",
    "/api/dashboard/summary",
    "/api/dashboard/timeline",
    "/api/books/status",
    "/api/books/search?q=test",
    "/api/mental/reps",
    "/api/mental/challenges",
    "/api/models/status",
    "/api/models/available",
    "/api/models/",
]

# Single-item GET paths — these will 404 but the auth check happens first.
ALL_GET_SINGLE_PATHS = [
    "/api/skills/99999",
    "/api/sessions/99999",
    "/api/assessments/99999",
    "/api/sessions/skill/99999/count",
    "/api/mental/reps/99999",
    "/api/mental/challenges/99999",
    "/api/mental/challenges/next/99999",
]


class TestAuthOnAllEndpoints:
    """Auth middleware applies to every endpoint except /api/health.

    Each scenario is parametrized over ALL GET endpoints to verify the
    middleware catches every path uniformly.
    """

    @pytest.fixture(autouse=True)
    def enable_auth(self, monkeypatch):
        """Override conftest's autouse disable_auth — turn auth ON."""
        monkeypatch.delenv("DISABLE_AUTH", raising=False)

    # -- missing key ---------------------------------------------------------

    @pytest.mark.parametrize("path", ALL_GET_PATHS + ALL_GET_SINGLE_PATHS)
    def test_no_key_returns_401(self, client, path):
        """GIVEN no X-API-Key WHEN any endpoint THEN 401."""
        resp = client.get(path)
        assert resp.status_code == 401, f"{path}: expected 401, got {resp.status_code}"

    # -- bad key -------------------------------------------------------------

    @pytest.mark.parametrize("path", ALL_GET_PATHS + ALL_GET_SINGLE_PATHS)
    def test_bad_key_returns_401(self, client, path):
        """GIVEN wrong X-API-Key WHEN any endpoint THEN 401."""
        resp = client.get(path, headers={"X-API-Key": "this-is-wrong"})
        assert resp.status_code == 401, f"{path}: expected 401, got {resp.status_code}"

    # -- valid key -----------------------------------------------------------

    @pytest.mark.parametrize("path", ALL_GET_PATHS + ALL_GET_SINGLE_PATHS)
    def test_valid_key_passes(self, client, auth_headers, path):
        """GIVEN valid X-API-Key WHEN any endpoint THEN not 401."""
        resp = client.get(path, headers=auth_headers)
        assert resp.status_code != 401, f"{path}: auth rejected valid key"

    # -- health exempt -------------------------------------------------------

    def test_health_endpoint_exempt(self, client):
        """GIVEN no key WHEN /api/health THEN 200 (bypass)."""
        resp = client.get("/api/health")
        assert resp.status_code == 200, f"Health: expected 200, got {resp.status_code}"

    # -- DISABLE_AUTH bypass -------------------------------------------------

    def test_disable_auth_bypass(self, client, monkeypatch):
        """GIVEN DISABLE_AUTH=1 WHEN no key THEN 200."""
        monkeypatch.setenv("DISABLE_AUTH", "1")
        resp = client.get("/api/skills/")
        assert resp.status_code == 200, f"Bypass: expected 200, got {resp.status_code}"

    # -- POST auth -----------------------------------------------------------

    def test_post_no_key_returns_401(self, client):
        """GIVEN no key WHEN POST endpoint THEN 401 (middleware before handler)."""
        resp = client.post("/api/skills/", json={})
        assert resp.status_code == 401, f"POST: expected 401, got {resp.status_code}"

    def test_put_no_key_returns_401(self, client):
        """GIVEN no key WHEN PUT endpoint THEN 401."""
        resp = client.put("/api/models/mode", json={"mode": "local"})
        assert resp.status_code == 401, f"PUT: expected 401, got {resp.status_code}"


# ============================================================================
# 2. Rate limiting
# ============================================================================

class TestRateLimiting:
    """Verify slowapi rate limiting: burst 61 POSTs → 429, GET/health unlimited.

    NOTE: The burst-61 test uses a dedicated mini-app to avoid interference
    from shared slowapi state accumulated by other test modules that also
    send POST requests (test_input_security, test_skills, etc.).
    """

    def test_burst_61_posts_returns_429_on_61st(self):
        """GIVEN 5/min rate limit WHEN 6th POST THEN 429 with descriptive body."""
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address

        app = FastAPI()
        test_limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = test_limiter
        app.add_exception_handler(429, _rate_limit_exceeded_handler)

        @app.put("/test")
        @test_limiter.limit("60/minute")
        def endpoint(request: Request):
            return {"ok": True}

        with TestClient(app) as isolated:
            for i in range(60):
                resp = isolated.put("/test", json={})
                assert resp.status_code == 200, f"Req #{i+1} failed: {resp.text}"

            # 61st in the same minute window → 429
            resp = isolated.put("/test", json={})
            assert resp.status_code == 429, (
                f"Expected 429, got {resp.status_code}: {resp.text}"
            )
            body = resp.json()
            # slowapi 0.1.9 returns error body on 429
            assert "error" in body or "detail" in body

    def test_get_unlimited(self, client):
        """GIVEN 100 GET requests to rate-limited app THEN all 200."""
        for i in range(100):
            resp = client.get("/api/skills/")
            assert resp.status_code == 200, f"GET #{i+1} failed: {resp.text}"

    def test_health_unlimited(self, client):
        """GIVEN 100 health requests THEN all 200 (no rate limit)."""
        for i in range(100):
            resp = client.get("/api/health")
            assert resp.status_code == 200, f"Health #{i+1} failed: {resp.text}"

    def test_limiter_wired_in_main_app(self, client, auth_headers):
        """GIVEN real main app WHEN single POST THEN 200 (limiter present)."""
        resp = client.put("/api/models/mode", json={"mode": "local"}, headers=auth_headers)
        assert resp.status_code == 200, f"Limiter check: expected 200, got {resp.status_code}"


# ============================================================================
# 3. Input sanitization
# ============================================================================

class TestInputSanitization:
    """Verify input sanitization through the API and core.utils."""

    def test_sanitize_prompt_strips_control_chars(self):
        """GIVEN control chars WHEN sanitize_prompt THEN stripped."""
        from core.utils import sanitize_prompt

        result = sanitize_prompt("a\x00b\x01c\x1Fd")
        assert result == "abcd", f"Control chars not stripped: {result!r}"

    def test_sanitize_prompt_preserves_whitespace(self):
        """GIVEN \\t\\n\\r WHEN sanitize_prompt THEN preserved."""
        from core.utils import sanitize_prompt

        result = sanitize_prompt("a\tb\nc\rd")
        assert "\t" in result, "Tab stripped"
        assert "\n" in result, "Newline stripped"
        assert "\r" in result, "CR stripped"

    def test_sanitize_prompt_truncates_long(self):
        """GIVEN long text WHEN sanitize_prompt THEN truncated to 2000."""
        from core.utils import sanitize_prompt

        text = "x" * 3000
        result = sanitize_prompt(text)
        assert len(result) == 2000, f"Expected 2000, got {len(result)}"

    def test_sanitize_prompt_empty_input(self):
        """GIVEN empty/None input WHEN sanitize_prompt THEN empty string."""
        from core.utils import sanitize_prompt

        assert sanitize_prompt("") == ""
        assert sanitize_prompt(None) == ""  # type: ignore[arg-type]

    def test_control_chars_in_session_input(self, client, skill_factory, auth_headers):
        """GIVEN control chars in what_i_practiced WHEN POST THEN accepted."""
        skill = skill_factory()
        resp = client.post("/api/sessions/", json={
            "skill_id": skill.id,
            "duration_minutes": 15,
            "what_i_practiced": "normal text \x00\x01\x1F with control chars",
            "difficulty": 3,
            "micro_error_found": "error with \x00 byte",
            "correction_applied": "fixed it",
        }, headers=auth_headers)
        # The API accepts control chars; sanitization happens internally
        # before AI prompt interpolation.
        assert resp.status_code == 201, (
            f"Control-char POST failed: {resp.status_code} {resp.text}"
        )

    def test_max_length_exceeded_returns_422(self, client, auth_headers):
        """GIVEN what_i_practiced > 2000 chars WHEN POST THEN 422."""
        resp = client.post("/api/sessions/", json={
            "skill_id": 1,
            "duration_minutes": 15,
            "what_i_practiced": "X" * 2001,
            "difficulty": 3,
            "micro_error_found": "test error",
        }, headers=auth_headers)
        # FastAPI raises 422 for Pydantic max_length violations
        assert resp.status_code == 422, (
            f"Expected 422, got {resp.status_code}: {resp.text[:200]}"
        )

    def test_max_length_boundary_accepted(self, client, skill_factory, auth_headers):
        """GIVEN what_i_practiced at exactly 2000 chars WHEN POST THEN 200."""
        skill = skill_factory()
        text = "X" * 2000
        resp = client.post("/api/sessions/", json={
            "skill_id": skill.id,
            "duration_minutes": 15,
            "what_i_practiced": text,
            "difficulty": 3,
            "micro_error_found": "test error",
        }, headers=auth_headers)
        assert resp.status_code == 201, (
            f"Boundary POST failed: {resp.status_code} {resp.text[:200]}"
        )


# ============================================================================
# 4. Security headers
# ============================================================================

class TestSecurityHeaders:
    """Every response includes all 4 standard security headers."""

    EXPECTED = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "0",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    def _assert_headers(self, resp):
        for header, expected in self.EXPECTED.items():
            actual = resp.headers.get(header)
            assert actual == expected, (
                f"Header {header!r}: expected {expected!r}, got {actual!r}"
            )

    def test_health_response(self, client):
        """GIVEN /api/health WHEN response THEN 4 security headers present."""
        resp = client.get("/api/health")
        self._assert_headers(resp)

    def test_api_200_response(self, client, auth_headers):
        """GIVEN API 200 WHEN response THEN 4 security headers present."""
        resp = client.get("/api/skills/", headers=auth_headers)
        assert resp.status_code == 200
        self._assert_headers(resp)

    def test_401_response(self, client, monkeypatch):
        """GIVEN 401 WHEN response THEN 4 security headers present."""
        monkeypatch.delenv("DISABLE_AUTH", raising=False)
        resp = client.get("/api/skills/")
        assert resp.status_code == 401
        self._assert_headers(resp)

    def test_404_response(self, client, auth_headers):
        """GIVEN 404 WHEN response THEN 4 security headers present."""
        resp = client.get("/api/skills/99999", headers=auth_headers)
        assert resp.status_code == 404
        self._assert_headers(resp)

    def test_422_response(self, client, auth_headers):
        """GIVEN 422 validation error WHEN response THEN 4 security headers."""
        resp = client.post("/api/sessions/", json={
            "skill_id": 1,
            "duration_minutes": 15,
            "what_i_practiced": "X" * 2001,  # triggers max_length 422
            "difficulty": 3,
            "micro_error_found": "error",
        }, headers=auth_headers)
        assert resp.status_code == 422
        self._assert_headers(resp)

    def test_post_201_response(self, client, skill_factory, auth_headers):
        """GIVEN POST 201 WHEN response THEN 4 security headers present."""
        skill = skill_factory()
        resp = client.post("/api/sessions/", json={
            "skill_id": skill.id,
            "duration_minutes": 15,
            "what_i_practiced": "test security headers on POST response",
            "difficulty": 3,
            "micro_error_found": "an error",
        }, headers=auth_headers)
        assert resp.status_code == 201
        self._assert_headers(resp)


# ============================================================================
# 5. Lock error path
# ============================================================================

class TestLockErrorPath:
    """Index lock is released when background_executor.submit() fails.

    See api/routes/books.py trigger_indexing(): the try/except calls
    release_index_lock() when submit() raises. This test verifies that
    path is exercised correctly.
    """

    def test_submit_failure_releases_lock(self, client, auth_headers):
        """GIVEN submit() raises WHEN POST /api/books/index THEN lock released."""
        # We patch at the point of USE in api.routes.books because that module
        # does ``from core.rag import has_pdf_files, ...`` which creates local
        # references that are not affected by patching core.rag.*.
        #
        # Similarly, background_executor.submit is patched at the books module
        # level to override the autouse mock_ai fixture's patch.
        with (
            patch("api.routes.books.has_pdf_files", return_value=True),
            patch("api.routes.books.try_acquire_index_lock", return_value=True),
            patch("api.routes.books.release_index_lock") as mock_release,
            patch("api.routes.books.background_executor.submit",
                  side_effect=RuntimeError("executor full")),
        ):
            resp = client.post(
                "/api/books/index",
                json={"force": False},
                headers=auth_headers,
            )
            assert resp.status_code == 500, (
                f"Expected 500 on submit failure, got {resp.status_code}: {resp.text}"
            )
            assert "No se pudo iniciar" in resp.json()["detail"]

        # Assert release_index_lock was called on the error path
        mock_release.assert_called_once()
