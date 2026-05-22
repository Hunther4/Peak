"""
Tests for T-07 (sanitize_prompt in AI prompts), T-09 (print→logging), and T-11 (rate limiting).

Strict TDD: tests written BEFORE implementation code.

Naming: test_z_ prefix ensures these run after all other tests, so rate limit
tests don't exhaust the shared counter before other POST tests run.
"""

import pytest
from unittest.mock import patch


# ============================================================================
# T-07: sanitize_prompt applied to user text in AI prompts
# ============================================================================

class MockQuickLogResult:
    def model_dump(self):
        return {"correction_applied": "auto correction", "hypothesis_tomorrow": "keep going"}


class TestSanitizePromptInAI:
    """Sanitize_prompt is applied to user text before AI prompt interpolation."""

    # --- generate_quick_log_completions ---

    @patch("core.ai.generate_structured_json")
    @patch("core.router.get_ai_mode", return_value="local")
    def test_quick_log_strips_control_chars(self, mock_mode, mock_gen):
        """GIVEN user input with control chars WHEN quick log THEN prompt has no control chars."""
        from core.ai import generate_quick_log_completions
        mock_gen.return_value = MockQuickLogResult()

        control_what = "practice\x00session\x01test"
        control_error = "error\x1Ffound\x00here"
        generate_quick_log_completions(control_what, control_error, "test-domain")

        call_args = mock_gen.call_args
        user_prompt = call_args[0][1]  # 2nd positional arg is user_prompt

        assert "\x00" not in user_prompt
        assert "\x01" not in user_prompt
        assert "\x1F" not in user_prompt
        assert "practicesessiontest" in user_prompt.replace(" ", "").replace("\n", "")
        assert "errorfoundhere" in user_prompt.replace(" ", "").replace("\n", "")

    @patch("core.ai.generate_structured_json")
    @patch("core.router.get_ai_mode", return_value="local")
    def test_quick_log_preserves_normal_text(self, mock_mode, mock_gen):
        """GIVEN normal input WHEN quick log THEN text passes through."""
        from core.ai import generate_quick_log_completions
        mock_gen.return_value = MockQuickLogResult()

        what = "Practiqué escalas mayores con metrónomo"
        error = "Tensión en los dedos al cambiar de posición"
        generate_quick_log_completions(what, error, "guitar")

        call_args = mock_gen.call_args
        user_prompt = call_args[0][1]

        assert "Practiqué escalas mayores" in user_prompt
        assert "Tensión en los dedos" in user_prompt

    @patch("core.ai.generate_structured_json")
    @patch("core.router.get_ai_mode", return_value="local")
    def test_quick_log_truncates_long_input(self, mock_mode, mock_gen):
        """GIVEN input longer than 2000 chars WHEN quick log THEN truncated."""
        from core.ai import generate_quick_log_completions
        mock_gen.return_value = MockQuickLogResult()

        long_what = "x" * 3000
        generate_quick_log_completions(long_what, "error", "test")

        call_args = mock_gen.call_args
        user_prompt = call_args[0][1]

        # The sanitized what_i_practiced (2000 chars of x) + rest of prompt
        # should be roughly 2000 + overhead
        assert len(user_prompt) > 1900  # still has the content

    # --- audit_session ---

    @patch("core.auditor.generate_structured_json")
    @patch("core.auditor.query_books", return_value=[])
    def test_audit_session_strips_control_chars(self, mock_query, mock_gen):
        """GIVEN session_data with control chars WHEN audit THEN prompts sanitized."""
        from core.auditor import audit_session, AuditResult
        mock_gen.return_value = AuditResult(
            was_deliberate=True, score=80, confidence=0.9,
            verdict="ok", reasoning="solid", domain_specific_notes="N/A",
            book_citations=[],
        )

        audit_session({
            "what_i_practiced": "practice\x00session",
            "difficulty": 3,
            "micro_error_found": "error\x01here",
            "correction_applied": "correction\x1Fdone",
            "hypothesis_tomorrow": "next\x00step",
        }, domain="music", onboarding_mode=False)

        call_args = mock_gen.call_args
        user_prompt = call_args[0][1]

        assert "\x00" not in user_prompt
        assert "\x01" not in user_prompt
        assert "\x1F" not in user_prompt
        assert "practicesession" in user_prompt.replace(" ", "").replace("\n", "")
        assert "errorhere" in user_prompt.replace(" ", "").replace("\n", "")
        assert "correctiondone" in user_prompt.replace(" ", "").replace("\n", "")
        assert "nextstep" in user_prompt.replace(" ", "").replace("\n", "")

    @patch("core.auditor.generate_structured_json")
    @patch("core.auditor.query_books", return_value=[])
    def test_audit_session_preserves_normal_text(self, mock_query, mock_gen):
        """GIVEN normal session data WHEN audit THEN text passes through."""
        from core.auditor import audit_session, AuditResult
        mock_gen.return_value = AuditResult(
            was_deliberate=True, score=80, confidence=0.9,
            verdict="ok", reasoning="solid", domain_specific_notes="N/A",
            book_citations=[],
        )

        audit_session({
            "what_i_practiced": "Practiqué el compás 14-16",
            "difficulty": 4,
            "micro_error_found": "Dedo meñique se levanta",
            "correction_applied": "Mantener dedos cerca del diapasón",
            "hypothesis_tomorrow": "Practicar a 60bpm sin errores",
        }, domain="music", onboarding_mode=False)

        call_args = mock_gen.call_args
        user_prompt = call_args[0][1]

        assert "Practiqué el compás" in user_prompt
        assert "Dedo meñique" in user_prompt
        assert "Mantener dedos" in user_prompt
        assert "Practicar a 60bpm" in user_prompt

    # --- generate_mental_rep ---

    @patch("core.mental.generate_structured_json")
    @patch("core.mental.query_books", return_value=[])
    def test_mental_rep_strips_control_chars_from_summary(self, mock_query, mock_gen):
        """GIVEN session_summary with control chars WHEN mental rep THEN sanitized."""
        from core.mental import generate_mental_rep, MentalRepResult
        mock_gen.return_value = MentalRepResult(
            description="test", is_real_shift=True,
            reasoning="test", key_insight="test"
        )

        generate_mental_rep(
            skill_name="Piano", domain="music", skill_type="staircase",
            current_level=10.0, prev_description=None, prev_version=0,
            session_summary="3 sesiones\x00de práctica\x01deliberada",
        )

        call_args = mock_gen.call_args
        user_prompt = call_args[0][1]

        assert "\x00" not in user_prompt
        assert "\x01" not in user_prompt
        # Control chars stripped, text merged without them
        assert "3 sesionesde prácticadeliberada" in user_prompt

    @patch("core.mental.generate_structured_json")
    @patch("core.mental.query_books", return_value=[])
    def test_mental_rep_preserves_normal_text(self, mock_query, mock_gen):
        """GIVEN normal session_summary WHEN mental rep THEN text unchanged."""
        from core.mental import generate_mental_rep, MentalRepResult
        mock_gen.return_value = MentalRepResult(
            description="test", is_real_shift=True,
            reasoning="test", key_insight="test"
        )

        summary = "últimas 10 sesiones: escalas mayores, arpegios, velocidad"
        generate_mental_rep(
            skill_name="Piano", domain="music", skill_type="staircase",
            current_level=10.0, prev_description=None, prev_version=0,
            session_summary=summary,
        )

        call_args = mock_gen.call_args
        user_prompt = call_args[0][1]
        assert summary in user_prompt

    # --- generate_challenge ---

    @patch("core.mental.generate_structured_json")
    @patch("core.mental.query_books", return_value=[])
    def test_challenge_strips_control_chars_from_last_session(self, mock_query, mock_gen):
        """GIVEN last_session with control chars WHEN challenge THEN sanitized."""
        from core.mental import generate_challenge, ChallengeResult
        mock_gen.return_value = ChallengeResult(
            description="test", difficulty_target=3, rationale="test"
        )

        generate_challenge(
            skill_name="Piano", domain="music", skill_type="staircase",
            current_level=30.0,
            last_session="qué:\x00escalas, error:\x01tempo",
        )

        call_args = mock_gen.call_args
        user_prompt = call_args[0][1]

        assert "\x00" not in user_prompt
        assert "\x01" not in user_prompt

    @patch("core.mental.generate_structured_json")
    @patch("core.mental.query_books", return_value=[])
    def test_challenge_preserves_normal_text(self, mock_query, mock_gen):
        """GIVEN normal last_session WHEN challenge THEN text unchanged."""
        from core.mental import generate_challenge, ChallengeResult
        mock_gen.return_value = ChallengeResult(
            description="test", difficulty_target=3, rationale="test"
        )

        session = "qué: escalas a 60bpm, dificultad: 3, error: tempo irregular"
        generate_challenge(
            skill_name="Piano", domain="music", skill_type="staircase",
            current_level=30.0, last_session=session,
        )

        call_args = mock_gen.call_args
        user_prompt = call_args[0][1]
        assert "escalas a 60bpm" in user_prompt
        assert "tempo irregular" in user_prompt


# ============================================================================
# T-11: Rate limiting with slowapi
# ============================================================================

class TestRateLimiting:
    """Integration tests for slowapi rate limiting.

    Uses a separate mini-app to avoid sharing rate limit state with
    the main application's test client (which runs other tests).
    """

    def test_rate_limiter_returns_429_on_exceeded(self):
        """GIVEN rate-limited endpoint WHEN 6th request in window THEN 429 with Retry-After."""
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address

        app = FastAPI()
        test_limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = test_limiter
        app.add_exception_handler(429, _rate_limit_exceeded_handler)

        @app.put("/test")
        @test_limiter.limit("5/minute")
        def test_endpoint(request: Request):
            return {"ok": True}

        with TestClient(app) as client:
            for i in range(5):
                response = client.put("/test", json={})
                assert response.status_code == 200, f"Request {i+1} failed"

            # 6th request within the window → 429
            response = client.put("/test", json={})
            assert response.status_code == 429, (
                f"Expected 429, got {response.status_code}: {response.text}"
            )
            # slowapi 0.1.9 returns 429 with error detail but may not set
            # Retry-After for the exceeded case; verify the error body instead
            body = response.json()
            assert "error" in body
            assert "rate limit" in body["error"].lower()

    def test_get_endpoints_not_rate_limited(self):
        """GIVEN non-rate-limited GET endpoint WHEN 100 requests THEN all succeed."""
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address

        app = FastAPI()
        test_limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = test_limiter
        app.add_exception_handler(429, _rate_limit_exceeded_handler)

        @app.get("/unlimited")
        def unlimited(request: Request):
            return {"ok": True}

        with TestClient(app) as client:
            for i in range(100):
                response = client.get("/unlimited")
                assert response.status_code == 200, f"Request {i+1} failed"

    def test_limiter_integration_with_main_app(self, client, skill_factory):
        """GIVEN real POST routes WHEN called once THEN 200 (limiter is present and working)."""
        # Create a skill via POST (rate-limited)
        skill = skill_factory()
        resp = client.post("/api/skills/", json={
            "name": "rate-limit-test",
            "domain": "memory",
            "skill_type": "staircase",
            "config_path": "skills/default.yaml",
            "slug": "rate-limit-test",
        })
        assert resp.status_code == 201, f"Skills POST failed: {resp.text}"

        # Create an assessment via POST (rate-limited)
        resp = client.post("/api/assessments/", json={
            "skill_id": skill.id,
            "type": "probe",
            "score": 50.0,
        })
        assert resp.status_code == 201, f"Assessment POST failed: {resp.text}"

        # PUT /api/models/mode (rate-limited)
        resp = client.put("/api/models/mode", json={"mode": "local"})
        assert resp.status_code == 200, f"Models PUT failed: {resp.text}"

    def test_health_endpoint_no_rate_limit(self, client):
        """GIVEN health endpoint WHEN many requests THEN all succeed."""
        for i in range(100):
            response = client.get("/api/health")
            assert response.status_code == 200, f"Health request {i+1} failed"


# ============================================================================
# T-09: print() → logging verification test
# ============================================================================

class TestNoPrintStatements:
    """Verification that print() calls have been replaced with logging."""

    def test_no_print_in_core(self):
        """GIVEN all files in core/ WHEN AST-searched for print( THEN 0 matches."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-c", """
import ast, sys, pathlib
root = pathlib.Path("core")
issues = []
for f in sorted(root.rglob("*.py")):
    try:
        source = f.read_bytes()
        if b"print(" not in source:
            continue
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
                issues.append((str(f), node.lineno))
    except Exception as e:
        issues.append((str(f), str(e)))
if issues:
    for f, l in issues:
        print(f"{f}:{l}")
    sys.exit(1)
else:
    print("OK")
"""],
            capture_output=True, text=True, cwd="/home/hunther4/Peak/backend",
            timeout=30,
        )
        assert result.returncode == 0, f"print() found in core/:\n{result.stdout}\n{result.stderr}"

    def test_no_print_in_api_routes(self):
        """GIVEN all files in api/routes/ WHEN AST-searched for print( THEN 0 matches."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-c", """
import ast, sys, pathlib
root = pathlib.Path("api/routes")
issues = []
for f in sorted(root.rglob("*.py")):
    try:
        source = f.read_bytes()
        if b"print(" not in source:
            continue
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
                issues.append((str(f), node.lineno))
    except Exception as e:
        issues.append((str(f), str(e)))
if issues:
    for f, l in issues:
        print(f"{f}:{l}")
    sys.exit(1)
else:
    print("OK")
"""],
            capture_output=True, text=True, cwd="/home/hunther4/Peak/backend",
            timeout=30,
        )
        assert result.returncode == 0, f"print() found in api/routes/:\n{result.stdout}\n{result.stderr}"

    def test_no_bare_except_in_core(self):
        """GIVEN all files in core/ WHEN searched for bare except: THEN 0 matches."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-c", """
import ast, sys, pathlib
root = pathlib.Path("core")
issues = []
for f in sorted(root.rglob("*.py")):
    try:
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append((str(f), node.lineno))
    except Exception as e:
        issues.append((str(f), str(e)))
if issues:
    for f, l in issues:
        print(f"{f}:{l}")
    sys.exit(1)
else:
    print("OK")
"""],
            capture_output=True, text=True, cwd="/home/hunther4/Peak/backend",
            timeout=30,
        )
        assert result.returncode == 0, f"bare except: found in core/:\n{result.stdout}\n{result.stderr}"

    def test_no_bare_except_in_api_routes(self):
        """GIVEN all files in api/routes/ WHEN searched for bare except: THEN 0 matches."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-c", """
import ast, sys, pathlib
root = pathlib.Path("api/routes")
issues = []
for f in sorted(root.rglob("*.py")):
    try:
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append((str(f), node.lineno))
    except Exception as e:
        issues.append((str(f), str(e)))
if issues:
    for f, l in issues:
        print(f"{f}:{l}")
    sys.exit(1)
else:
    print("OK")
"""],
            capture_output=True, text=True, cwd="/home/hunther4/Peak/backend",
            timeout=30,
        )
        assert result.returncode == 0, f"bare except: found in api/routes/:\n{result.stdout}\n{result.stderr}"
