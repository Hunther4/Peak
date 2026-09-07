"""
Tests for masked API key in startup log (T-05).

Strict TDD: tests written BEFORE production code.
"""
import logging


class TestMaskedApiKeyLog:
    """Verify API key is masked in log output."""

    def test_generated_key_logged_masked(self, monkeypatch, caplog):
        """GIVEN no env and no DB WHEN initialize generates key THEN log shows only first 4 chars."""
        from core.auth import LazyAPIKeyManager

        monkeypatch.delenv("PEAK_API_KEY", raising=False)

        manager = LazyAPIKeyManager()
        with caplog.at_level(logging.INFO):
            raw_key = manager.initialize()

        assert raw_key is not None
        assert len(raw_key) == 32

        # Find the relevant log record
        found = False
        for record in caplog.records:
            if "generated new key" in record.getMessage():
                found = True
                msg = record.getMessage()
                # Key should be masked: first 4 chars + "****"
                assert raw_key[:4] in msg
                assert "****" in msg
                # The full key should NOT appear in the log
                assert raw_key not in msg
                assert raw_key[4:] not in msg
                break
        assert found, "Expected log message not found"
