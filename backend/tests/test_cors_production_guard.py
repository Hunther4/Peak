"""
Tests for CORS `*` production guard (T-09).

Strict TDD: tests written BEFORE production code.
"""
from unittest.mock import patch

import pytest


class TestCorsProductionGuard:
    """Verify CORS_ORIGIN=* is rejected in production."""

    @pytest.fixture(autouse=True)
    def cleanup_env(self, monkeypatch):
        monkeypatch.delenv("PRODUCTION", raising=False)
        monkeypatch.delenv("CORS_ORIGIN", raising=False)

    def test_cors_wildcard_logs_warning(self, monkeypatch):
        """GIVEN CORS_ORIGIN=* WHEN app starts THEN warning is logged."""
        monkeypatch.setenv("CORS_ORIGIN", "*")

        from main import _check_cors_production_guard

        with patch("main.logger") as mock_logger:
            _check_cors_production_guard()

        # Should log warning about CORS_ORIGIN=*
        mock_logger.warning.assert_called_once()
        call_msg = mock_logger.warning.call_args[0][0]
        assert "CORS_ORIGIN" in call_msg
        assert "*" in call_msg

    def test_cors_wildcard_with_production_raises(self, monkeypatch):
        """GIVEN CORS_ORIGIN=* and PRODUCTION=1 WHEN check THEN RuntimeError."""
        monkeypatch.setenv("CORS_ORIGIN", "*")
        monkeypatch.setenv("PRODUCTION", "1")

        from main import _check_cors_production_guard

        with pytest.raises(RuntimeError) as exc:
            _check_cors_production_guard()
        assert "CORS_ORIGIN" in str(exc.value)
        assert "production" in str(exc.value).lower()

    def test_cors_wildcard_without_production_ok(self, monkeypatch):
        """GIVEN CORS_ORIGIN=* without PRODUCTION WHEN check THEN no error."""
        monkeypatch.setenv("CORS_ORIGIN", "*")

        from main import _check_cors_production_guard

        # Should not raise
        _check_cors_production_guard()

    def test_cors_specific_origin_no_warning(self, monkeypatch):
        """GIVEN CORS_ORIGIN set to specific origin WHEN check THEN no warning."""
        monkeypatch.setenv("CORS_ORIGIN", "https://example.com")

        from main import _check_cors_production_guard

        with patch("main.logger") as mock_logger:
            _check_cors_production_guard()
        mock_logger.warning.assert_not_called()
