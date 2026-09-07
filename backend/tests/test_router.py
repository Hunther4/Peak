from unittest.mock import patch

from pydantic import BaseModel

from core.router import execute_with_router, get_ai_mode, set_ai_mode


def test_ai_mode_roundtrip():
    # Test setting to 'api'
    set_ai_mode("api")
    assert get_ai_mode() == "api"

    # Test setting to 'local'
    set_ai_mode("local")
    assert get_ai_mode() == "local"

    # Test invalid mode (should fallback to 'local')
    set_ai_mode("invalid_mode")
    assert get_ai_mode() == "local"


class _Probe(BaseModel):
    answer: str


def test_local_mode_falls_back_to_api_when_lm_studio_is_down():
    """In local mode, if LM Studio fails, the call MUST fall back to API.

    Regression: previously local mode went directly to LM Studio with no
    fallback, causing 60-120s hangs in the audit, mental, and quick-log
    paths when LM Studio was down. Now those paths use the full fallback
    chain (LM Studio → Groq → OpenRouter) regardless of mode.
    """
    set_ai_mode("local")

    class _ApiResult(_Probe):
        pass

    captured = {"called_groq": False, "called_openrouter": False}

    def fake_groq(*args, **kwargs):
        captured["called_groq"] = True
        return _ApiResult(answer="from-groq")

    def fake_openrouter(*args, **kwargs):
        captured["called_openrouter"] = True
        return _ApiResult(answer="from-openrouter")

    def fake_lm_studio(*args, **kwargs):
        # Simulate LM Studio down — _try_lm_studio_with_retry catches
        # connection errors internally and returns None
        return None

    # Mock the model registry so the API fallback can find models
    fake_groq_model = type("M", (), {"provider": "groq", "model_id": "test-groq-model", "name": "Test Groq", "score": 90})()
    fake_or_model = type("M", (), {"provider": "openrouter", "model_id": "test-or-model", "name": "Test OR", "score": 80})()

    def fake_get_available_models(provider=None):
        if provider == "groq":
            return [fake_groq_model]
        if provider == "openrouter":
            return [fake_or_model]
        return []

    with patch("core.router._try_lm_studio_with_retry", side_effect=fake_lm_studio), \
         patch("core.router._call_groq", side_effect=fake_groq), \
         patch("core.router._call_openrouter", side_effect=fake_openrouter), \
         patch("core.model_registry.get_available_models", side_effect=fake_get_available_models):
        result = execute_with_router(
            task_type="audit",
            system_prompt="test",
            user_prompt="test",
            response_model=_Probe,
        )

    assert result is not None
    assert result.answer in ("from-groq", "from-openrouter")
    # Groq should be tried first in the API fallback chain
    assert captured["called_groq"] is True


def test_local_mode_returns_lm_studio_result_when_available():
    """In local mode, if LM Studio returns a valid result, use it (don't go to API)."""
    set_ai_mode("local")

    class _LmResult(_Probe):
        pass

    def fake_lm_studio(*args, **kwargs):
        return _LmResult(answer="from-lm-studio")

    captured_api_called = {"groq": False, "openrouter": False}

    def fake_groq(*args, **kwargs):
        captured_api_called["groq"] = True
        return _Probe(answer="from-groq")

    def fake_openrouter(*args, **kwargs):
        captured_api_called["openrouter"] = True
        return _Probe(answer="from-openrouter")

    with patch("core.router._try_lm_studio_with_retry", side_effect=fake_lm_studio), \
         patch("core.router._call_groq", side_effect=fake_groq), \
         patch("core.router._call_openrouter", side_effect=fake_openrouter):
        result = execute_with_router(
            task_type="audit",
            system_prompt="test",
            user_prompt="test",
            response_model=_Probe,
        )

    assert result is not None
    assert result.answer == "from-lm-studio"
    # API should NOT be called when LM Studio works
    assert captured_api_called["groq"] is False
    assert captured_api_called["openrouter"] is False
