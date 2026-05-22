"""
Tests para core/ai.py

Estrategia:
- generate_structured_json con force_local=True mockea client.chat.completions.create
  para no depender de LM Studio ni del router.
- generate_structured_json con force_local=False y modo "api" mockea
  get_ai_mode y execute_with_router para verificar que delega correctamente.
- generate_quick_log_completions mockea internamente para ver ambos modos.
"""
import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel, Field
from typing import Optional

from core.ai import generate_structured_json, generate_quick_log_completions, QuickLogCompletion


class _TestModel(BaseModel):
    name: str
    value: int


class _TestNestedModel(BaseModel):
    title: str
    items: list[int]


# ---------------------------------------------------------------------------
# generate_structured_json — Modo Local (force_local=True)
# ---------------------------------------------------------------------------

def _make_mock_response(content: str, choices_count: int = 1):
    """Construye un objeto simulando la respuesta de OpenAI."""
    choices = []
    for _ in range(choices_count):
        choice = MagicMock()
        choice.message.content = content
        choices.append(choice)
    response = MagicMock()
    response.choices = choices
    return response


@patch("core.ai.client.chat.completions.create")
def test_local_success_returns_parsed_model(mock_create):
    """Cuando LM Studio responde con JSON válido, retorna el modelo parseado."""
    mock_create.return_value = _make_mock_response('{"name": "foo", "value": 42}')

    result = generate_structured_json(
        "system prompt", "user prompt", _TestModel,
        force_local=True
    )

    assert result is not None
    assert isinstance(result, _TestModel)
    assert result.name == "foo"
    assert result.value == 42


@patch("core.ai.client.chat.completions.create")
def test_local_choices_empty_returns_none(mock_create):
    """Cuando choices viene vacío, retorna None."""
    mock_create.return_value = _make_mock_response("", choices_count=0)

    result = generate_structured_json(
        "system", "user", _TestModel, force_local=True
    )

    assert result is None


@patch("core.ai.client.chat.completions.create")
def test_local_empty_content_returns_none(mock_create):
    """Cuando message.content es None o vacío, retorna None."""
    mock_response = MagicMock()
    mock_response.choices = []
    choice = MagicMock()
    choice.message.content = None
    mock_response.choices = [choice]
    mock_create.return_value = mock_response

    result = generate_structured_json(
        "system", "user", _TestModel, force_local=True
    )

    assert result is None


@patch("core.ai.client.chat.completions.create")
def test_local_invalid_json_returns_none(mock_create):
    """Cuando la respuesta no es JSON válido, retorna None."""
    mock_create.return_value = _make_mock_response("esto no es json")

    result = generate_structured_json(
        "system", "user", _TestModel, force_local=True
    )

    assert result is None


@patch("core.ai.client.chat.completions.create")
def test_local_wrong_schema_returns_none(mock_create):
    """Cuando el JSON no matchea el esquema del modelo, retorna None."""
    mock_create.return_value = _make_mock_response('{"wrong": "data"}')

    result = generate_structured_json(
        "system", "user", _TestModel, force_local=True
    )

    assert result is None


@patch("core.ai.client.chat.completions.create")
def test_local_exception_returns_none(mock_create):
    """Cuando la llamada a LM Studio lanza excepción, retorna None."""
    mock_create.side_effect = Exception("Connection refused")

    result = generate_structured_json(
        "system", "user", _TestModel, force_local=True
    )

    assert result is None


@patch("core.ai.client.chat.completions.create")
def test_local_retries_on_failure(mock_create):
    """En el primer intento falla, en el segundo éxito."""
    mock_create.side_effect = [
        Exception("Timeout"),
        _make_mock_response('{"name": "ok", "value": 1}'),
    ]

    result = generate_structured_json(
        "system", "user", _TestModel,
        force_local=True, max_retries=2
    )

    assert result is not None
    assert result.name == "ok"
    assert mock_create.call_count == 2


@patch("core.ai.client.chat.completions.create")
def test_local_all_retries_fail_returns_none(mock_create):
    """Todos los reintentos fallan, retorna None."""
    mock_create.side_effect = Exception("Always fails")

    result = generate_structured_json(
        "system", "user", _TestModel,
        force_local=True, max_retries=3
    )

    assert result is None
    assert mock_create.call_count == 4  # max_retries + 1


@patch("core.ai.client.chat.completions.create")
def test_local_parses_cleaned_json(mock_create):
    """Responde con markdown wrapper y se limpia correctamente."""
    mock_create.return_value = _make_mock_response(
        '```json\n{"name": "test", "value": 99}\n```'
    )

    result = generate_structured_json(
        "system", "user", _TestModel, force_local=True
    )

    assert result is not None
    assert result.name == "test"
    assert result.value == 99


@patch("core.ai.client.chat.completions.create")
def test_local_nested_model(mock_create):
    """Funciona con modelos Pydantic anidados."""
    mock_create.return_value = _make_mock_response(
        '{"title": "List", "items": [1, 2, 3]}'
    )

    result = generate_structured_json(
        "system", "user", _TestNestedModel, force_local=True
    )

    assert result is not None
    assert result.title == "List"
    assert result.items == [1, 2, 3]


# ---------------------------------------------------------------------------
# generate_structured_json — Modo API (router delegado)
# ---------------------------------------------------------------------------

@patch("core.router.execute_with_router")
@patch("core.router.get_ai_mode")
def test_api_delegates_to_router(mock_get_mode, mock_execute):
    """En modo api, delega a execute_with_router con el task_type correcto."""
    mock_get_mode.return_value = "api"
    expected = _TestModel(name="from_router", value=7)
    mock_execute.return_value = expected

    result = generate_structured_json(
        "system", "user", _TestModel,
        task_type="assessment"
    )

    assert result is expected
    mock_execute.assert_called_once_with(
        "assessment", "system", "user", _TestModel
    )


@patch("core.router.execute_with_router")
@patch("core.router.get_ai_mode")
def test_api_default_task_type(mock_get_mode, mock_execute):
    """Por defecto task_type es 'audit'."""
    mock_get_mode.return_value = "api"
    expected = _TestModel(name="audit", value=0)
    mock_execute.return_value = expected

    result = generate_structured_json(
        "system", "user", _TestModel
    )

    assert result is expected
    mock_execute.assert_called_once_with(
        "audit", "system", "user", _TestModel
    )


@patch("core.router.execute_with_router")
@patch("core.router.get_ai_mode")
def test_local_mode_skips_router(mock_get_mode, mock_execute):
    """En modo local (no api), no llama al router."""
    mock_get_mode.return_value = "local"

    with patch("core.ai.client.chat.completions.create") as mock_create:
        mock_create.return_value = _make_mock_response('{"name": "x", "value": 1}')
        result = generate_structured_json(
            "system", "user", _TestModel
        )

    assert result is not None
    mock_execute.assert_not_called()


# ---------------------------------------------------------------------------
# generate_quick_log_completions
# ---------------------------------------------------------------------------

@patch("core.ai.generate_structured_json")
@patch("core.router.get_ai_mode")
def test_quick_log_local_mode(mock_get_mode, mock_generate):
    """En modo local, llama a generate_structured_json."""
    mock_get_mode.return_value = "local"
    mock_generate.return_value = QuickLogCompletion(
        correction_applied="Fixed posture",
        hypothesis_tomorrow="Keep shoulders down"
    )

    result = generate_quick_log_completions(
        "Scales", "Tension in shoulders", "guitar"
    )

    assert result["correction_applied"] == "Fixed posture"
    assert result["hypothesis_tomorrow"] == "Keep shoulders down"
    mock_generate.assert_called_once()


@patch("core.router.execute_with_router")
@patch("core.router.get_ai_mode")
def test_quick_log_api_mode(mock_get_mode, mock_execute):
    """En modo api, llama a execute_with_router con task_type quick_log."""
    mock_get_mode.return_value = "api"
    mock_execute.return_value = QuickLogCompletion(
        correction_applied="API fix",
        hypothesis_tomorrow="API tomorrow"
    )

    result = generate_quick_log_completions(
        "Practice", "Error", "domain"
    )

    assert result["correction_applied"] == "API fix"
    mock_execute.assert_called_once()


@patch("core.ai.generate_structured_json")
@patch("core.router.get_ai_mode")
def test_quick_log_fallback_on_failure(mock_get_mode, mock_generate):
    """Cuando falla la generación, retorna el dict de fallback."""
    mock_get_mode.return_value = "local"
    mock_generate.return_value = None

    result = generate_quick_log_completions(
        "X", "Y", "domain"
    )

    assert "No se pudo autogenerar" in result["correction_applied"]
    assert "Revisar sesión manualmente" in result["hypothesis_tomorrow"]
