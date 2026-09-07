"""
Tests for nonce-based CSP in SecurityHeadersMiddleware (T-07).

Strict TDD: tests written BEFORE production code.
"""
import re


class TestNonceCSP:
    """Verify CSP uses per-request nonces instead of unsafe-inline/eval."""

    CSP_NONCE_RE = re.compile(r"'nonce-([a-f0-9]+)'")

    def test_csp_contains_nonce(self, client):
        """GIVEN any response WHEN returned THEN CSP header uses nonce-based policy."""
        response = client.get("/api/health")
        csp = response.headers.get("Content-Security-Policy", "")
        assert "default-src 'self'" in csp
        assert "'nonce-" in csp
        assert "'unsafe-inline'" not in csp
        assert "'unsafe-eval'" not in csp

    def test_csp_nonce_is_hex_string(self, client):
        """GIVEN any response WHEN returned THEN nonce is a 32-char hex string."""
        response = client.get("/api/health")
        csp = response.headers.get("Content-Security-Policy", "")
        match = self.CSP_NONCE_RE.search(csp)
        assert match is not None
        nonce = match.group(1)
        assert len(nonce) == 32
        int(nonce, 16)  # raises ValueError if not hex

    def test_script_src_uses_nonce(self, client):
        """GIVEN any response WHEN returned THEN script-src uses nonce without unsafe-*."""
        response = client.get("/api/health")
        csp = response.headers.get("Content-Security-Policy", "")
        assert "script-src" in csp
        # Should contain 'nonce-...' but NOT 'unsafe-inline' or 'unsafe-eval'
        assert "'unsafe-inline'" not in csp
        assert "'unsafe-eval'" not in csp

    def test_style_src_uses_nonce(self, client):
        """GIVEN any response WHEN returned THEN style-src uses nonce without unsafe-inline."""
        response = client.get("/api/health")
        csp = response.headers.get("Content-Security-Policy", "")
        assert "style-src" in csp
        assert "'unsafe-inline'" not in csp

    def test_nonce_changes_per_request(self, client):
        """GIVEN two separate requests WHEN returned THEN nonces are different."""
        r1 = client.get("/api/health")
        r2 = client.get("/api/health")
        csp1 = r1.headers.get("Content-Security-Policy", "")
        csp2 = r2.headers.get("Content-Security-Policy", "")
        nonce1 = self.CSP_NONCE_RE.search(csp1).group(1)
        nonce2 = self.CSP_NONCE_RE.search(csp2).group(1)
        assert nonce1 != nonce2

    def test_csp_other_directives_preserved(self, client):
        """GIVEN any response WHEN returned THEN CSP still has img-src, font-src, etc."""
        response = client.get("/api/health")
        csp = response.headers.get("Content-Security-Policy", "")
        assert "img-src 'self' data: blob:" in csp
        assert "font-src 'self' data:" in csp
        assert "connect-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
