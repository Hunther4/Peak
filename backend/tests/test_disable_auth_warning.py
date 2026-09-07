"""
Tests for DISABLE_AUTH=1 warning log (T-08).

Strict TDD: tests written BEFORE production code.

We create a fresh TestClient inside the test so caplog captures
the lifespan log emission.
"""
import logging


class TestDisableAuthWarning:
    """Verify DISABLE_AUTH=1 triggers a warning log."""

    def test_disable_auth_logs_warning(self, caplog):
        """GIVEN DISABLE_AUTH=1 WHEN app starts THEN warning is logged.

        Create a fresh TestClient inside the test so caplog captures
        the lifespan log message.
        """
        import os
        os.environ["DISABLE_AUTH"] = "1"

        from fastapi.testclient import TestClient

        from main import app

        with caplog.at_level(logging.WARNING):
            with TestClient(app) as client:
                _ = client  # lifespan runs here
                pass

        found = False
        for record in caplog.records:
            if ("Authentication DISABLED" in record.getMessage()
                    and "API is open" in record.getMessage()):
                found = True
                break
        assert found, "Expected warning not found in caplog records"
