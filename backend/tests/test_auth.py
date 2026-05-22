"""
Tests for core/auth.py — API Key authentication middleware and manager.

Strict TDD: tests written BEFORE production code.
"""
import pytest


class TestLazyAPIKeyManager:
    """Unit tests for LazyAPIKeyManager — all exercise pure verify() logic."""

    def test_verify_correct_key_returns_true(self):
        """GIVEN cached hash WHEN verifying matching key THEN returns True."""
        from core.auth import LazyAPIKeyManager
        import bcrypt

        manager = LazyAPIKeyManager()
        raw = "test-key-123"
        hashed = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()
        manager._cached_hash = hashed

        assert manager.verify(raw) is True

    def test_verify_wrong_key_returns_false(self):
        """GIVEN cached hash WHEN verifying non-matching key THEN returns False."""
        from core.auth import LazyAPIKeyManager
        import bcrypt

        manager = LazyAPIKeyManager()
        hashed = bcrypt.hashpw(b"real-key", bcrypt.gensalt()).decode()
        manager._cached_hash = hashed

        assert manager.verify("wrong-key") is False

    def test_verify_empty_key_returns_false(self):
        """GIVEN cached hash WHEN verifying empty string THEN returns False."""
        from core.auth import LazyAPIKeyManager
        import bcrypt

        manager = LazyAPIKeyManager()
        hashed = bcrypt.hashpw(b"real-key", bcrypt.gensalt()).decode()
        manager._cached_hash = hashed

        assert manager.verify("") is False

    def test_verify_no_hash_cached_returns_false(self):
        """GIVEN no cached hash WHEN verifying any key THEN returns False."""
        from core.auth import LazyAPIKeyManager

        manager = LazyAPIKeyManager()
        assert manager._cached_hash is None
        assert manager.verify("any-key") is False

    def test_initialize_with_env_key_upserts_db(self, session, monkeypatch):
        """GIVEN PEAK_API_KEY env var WHEN initialize THEN hash stored in DB."""
        from core.auth import LazyAPIKeyManager
        from models.models import AppSetting
        from sqlmodel import select

        monkeypatch.setenv("PEAK_API_KEY", "from-env")
        manager = LazyAPIKeyManager()
        result = manager.initialize()

        assert result is None  # not newly generated
        assert manager._cached_hash is not None
        setting = session.exec(
            select(AppSetting).where(AppSetting.key == "api_key_hash")
        ).first()
        assert setting is not None
        assert setting.value == manager._cached_hash
        assert manager.verify("from-env") is True

    def test_initialize_generates_key_when_no_env_no_db(self, monkeypatch):
        """GIVEN no env and no DB WHEN initialize THEN generates 32-char hex key."""
        from core.auth import LazyAPIKeyManager
        monkeypatch.delenv("PEAK_API_KEY", raising=False)

        manager = LazyAPIKeyManager()
        result = manager.initialize()

        assert result is not None
        assert len(result) == 32
        assert manager._cached_hash is not None
        assert manager.verify(result) is True

    def test_verify_long_key_returns_true(self):
        """GIVEN cached hash for a very long key WHEN verifying THEN returns True."""
        from core.auth import LazyAPIKeyManager
        import bcrypt

        manager = LazyAPIKeyManager()
        raw = "a" * 256  # very long key
        hashed = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()
        manager._cached_hash = hashed

        assert manager.verify(raw) is True

    def test_initialize_twice_is_idempotent(self, monkeypatch):
        """GIVEN initialized manager WHEN initialize() is called again THEN no error."""
        from core.auth import LazyAPIKeyManager
        monkeypatch.delenv("PEAK_API_KEY", raising=False)

        manager = LazyAPIKeyManager()
        first = manager.initialize()
        second = manager.initialize()

        # Second call should not raise and should be consistent
        assert manager._cached_hash is not None
        if first is not None:
            assert manager.verify(first) is True
            assert second is None  # already exists

    def test_initialize_uses_existing_db_key(self, session, monkeypatch):
        """GIVEN key in DB and no env WHEN initialize THEN loads existing key."""
        from core.auth import LazyAPIKeyManager
        monkeypatch.delenv("PEAK_API_KEY", raising=False)
        from models.models import AppSetting
        import bcrypt

        raw = "existing-key"
        hashed = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()
        session.add(AppSetting(key="api_key_hash", value=hashed))
        session.commit()

        manager = LazyAPIKeyManager()
        result = manager.initialize()

        assert result is None
        assert manager._cached_hash == hashed
        assert manager.verify(raw) is True


class TestAuthIntegration:
    """Integration tests for AuthMiddleware via TestClient."""

    @pytest.fixture(autouse=True)
    def enable_auth(self, monkeypatch):
        """Override the autouse disable_auth fixture — auth is ON for these tests."""
        monkeypatch.delenv("DISABLE_AUTH", raising=False)

    def test_missing_key_returns_401(self, client):
        """GIVEN no X-API-Key WHEN calling any endpoint THEN 401."""
        response = client.get("/api/skills/")
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or missing API key"}

    def test_invalid_key_returns_401(self, client, api_key):
        """GIVEN wrong X-API-Key WHEN calling endpoint THEN 401."""
        response = client.get("/api/skills/", headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or missing API key"}

    def test_valid_key_returns_200(self, client, api_key):
        """GIVEN valid X-API-Key WHEN calling endpoint THEN 200."""
        response = client.get("/api/skills/", headers={"X-API-Key": api_key})
        assert response.status_code == 200

    def test_health_endpoint_exempt(self, client):
        """GIVEN no key WHEN calling /api/health THEN 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_disable_auth_bypass(self, client, monkeypatch):
        """GIVEN DISABLE_AUTH=1 WHEN calling without key THEN 200."""
        monkeypatch.setenv("DISABLE_AUTH", "1")
        response = client.get("/api/skills/")
        assert response.status_code == 200
