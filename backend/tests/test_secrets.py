"""
Tests for Secrets Management (T-04, T-05).

Strict TDD: tests written BEFORE production code.
"""
import pytest


class TestLazyAIClient:
    """Unit tests for lazy OpenAI client init in core/ai.py."""

    @pytest.fixture(autouse=True)
    def reset_ai_client(self):
        """Reset the lazy client cache before each test."""
        import core.ai
        core.ai._client = None
        yield

    def test_client_is_none_before_first_access(self):
        """GIVEN core.ai module loaded
        WHEN no get_client() call made yet THEN _client is None."""
        import core.ai
        assert core.ai._client is None

    def test_get_client_first_call_reads_env(self, monkeypatch):
        """GIVEN LM_STUDIO env vars set
        WHEN get_client() called first time THEN reads from env."""
        import core.ai

        monkeypatch.setenv("LM_STUDIO_API_KEY", "test-key-123")
        monkeypatch.setenv("LM_STUDIO_BASE_URL", "http://test.local:9999/v1")
        monkeypatch.setenv("LM_STUDIO_TIMEOUT", "45")

        client = core.ai.get_client()
        assert client.api_key == "test-key-123"
        # base_url is delegated to the internal httpx client
        assert "test.local:9999/v1" in str(client.base_url)

    def test_get_client_returns_same_instance_on_second_call(self, monkeypatch):
        """GIVEN get_client() called once
        WHEN called again THEN returns same cached instance."""
        import core.ai

        monkeypatch.setenv("LM_STUDIO_API_KEY", "cached-key")
        monkeypatch.setenv("LM_STUDIO_BASE_URL", "http://cached:1234/v1")
        monkeypatch.setenv("LM_STUDIO_TIMEOUT", "30")

        first = core.ai.get_client()
        # Change env — should NOT affect the cached client
        monkeypatch.setenv("LM_STUDIO_API_KEY", "different-key")
        second = core.ai.get_client()

        assert second is first
        assert second.api_key == "cached-key"  # not "different-key"

    def test_get_client_uses_defaults_when_env_missing(self, monkeypatch):
        """GIVEN no LM_STUDIO env vars set
        WHEN get_client() called THEN uses documented defaults."""
        import core.ai

        # Ensure env vars are absent
        monkeypatch.delenv("LM_STUDIO_API_KEY", raising=False)
        monkeypatch.delenv("LM_STUDIO_BASE_URL", raising=False)
        monkeypatch.delenv("LM_STUDIO_TIMEOUT", raising=False)

        client = core.ai.get_client()
        assert client.api_key == "lm-studio"
        assert "localhost:1234/v1" in str(client.base_url)


class TestLazyRouterKeys:
    """Unit tests for lazy API key accessors in core/router.py."""

    def test_get_groq_key_first_call_reads_env(self, monkeypatch):
        """GIVEN GROQ_API_KEY set in env
        WHEN _get_groq_key() called first time THEN returns env value."""
        from core.router import _get_groq_key, _key_cache
        _key_cache.clear()

        monkeypatch.setenv("GROQ_API_KEY", "gsk-test-groq")
        assert _get_groq_key() == "gsk-test-groq"

    def test_get_groq_key_caches_after_first_read(self, monkeypatch):
        """GIVEN _get_groq_key() called once
        WHEN called again with different env THEN returns cached value."""
        from core.router import _get_groq_key, _key_cache
        _key_cache.clear()

        monkeypatch.setenv("GROQ_API_KEY", "gsk-original")
        first = _get_groq_key()

        monkeypatch.setenv("GROQ_API_KEY", "gsk-changed")
        second = _get_groq_key()

        assert second == "gsk-original"

    def test_get_openrouter_key_first_call_reads_env(self, monkeypatch):
        """GIVEN OPENROUTER_API_KEY set in env
        WHEN _get_openrouter_key() called first time THEN returns env value."""
        from core.router import _get_openrouter_key, _key_cache
        _key_cache.clear()

        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-test")
        assert _get_openrouter_key() == "sk-or-v1-test"

    def test_get_openrouter_key_caches_after_first_read(self, monkeypatch):
        """GIVEN _get_openrouter_key() called once
        WHEN called again with different env THEN returns cached value."""
        from core.router import _get_openrouter_key, _key_cache
        _key_cache.clear()

        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-original")
        first = _get_openrouter_key()

        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-changed")
        second = _get_openrouter_key()

        assert second == "sk-or-v1-original"

    def test_both_keys_independently_cached(self, monkeypatch):
        """GIVEN both API keys in env
        WHEN both accessors called THEN each caches independently."""
        from core.router import (_get_groq_key, _get_openrouter_key,
                                 _key_cache)
        _key_cache.clear()

        monkeypatch.setenv("GROQ_API_KEY", "groq-only")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-only")

        groq_v1 = _get_groq_key()
        or_v1 = _get_openrouter_key()

        monkeypatch.setenv("GROQ_API_KEY", "groq-changed")
        monkeypatch.setenv("OPENROUTER_API_KEY", "or-changed")

        assert _get_groq_key() == "groq-only"
        assert _get_openrouter_key() == "or-only"
