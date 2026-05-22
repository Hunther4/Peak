"""
Tests para core/auditor.py

Auditoría de sesiones de práctica deliberada.
"""
import pytest
from unittest.mock import patch
from pydantic import BaseModel
from core.auditor import audit_session, AuditResult


@patch("core.auditor.generate_structured_json")
@patch("core.auditor.query_books")
def test_audit_session_success(mock_query, mock_gen):
    """auditoría exitosa retorna AuditResult con datos de IA."""
    mock_query.return_value = []
    mock_result = AuditResult(
        was_deliberate=True,
        score=85,
        confidence=0.9,
        verdict="Buena sesión",
        reasoning="Práctica enfocada",
        domain_specific_notes="N/A",
        book_citations=[]
    )
    mock_gen.return_value = mock_result

    result = audit_session({
        "what_i_practiced": "Practicar escala de Do mayor",
        "difficulty": 4,
        "micro_error_found": "Pulgar al pasar de 3 a 4",
        "correction_applied": "Levantar más el pulgar",
        "hypothesis_tomorrow": "Practicar transiciones de pulgar"
    }, domain="music", onboarding_mode=False)

    assert result is not None
    assert result.was_deliberate is True
    assert result.score == 85
    mock_gen.assert_called_once()


@patch("core.auditor.generate_structured_json")
@patch("core.auditor.query_books")
def test_audit_session_ai_fails(mock_query, mock_gen):
    """Cuando la IA falla, retorna AuditResult con fallback seguro."""
    mock_query.return_value = []
    mock_gen.return_value = None

    result = audit_session({
        "what_i_practiced": "algo vago",
        "difficulty": 2,
        "micro_error_found": "no sé",
        "correction_applied": "ninguna",
        "hypothesis_tomorrow": "nada"
    }, domain="generic", onboarding_mode=False)

    assert result is not None
    assert result.was_deliberate is False
    assert result.score == 1
    assert result.confidence == 0.0
    assert "Error de Auditoría" in result.verdict


@patch("core.auditor.generate_structured_json")
@patch("core.auditor.query_books")
def test_audit_session_onboarding_mode(mock_query, mock_gen):
    """En onboarding, el verdict tiene prefijo especial."""
    mock_query.return_value = []
    mock_result = AuditResult(
        was_deliberate=False,
        score=40,
        confidence=0.7,
        verdict="Sesión débil",
        reasoning="Falta especificidad",
        domain_specific_notes="N/A",
        book_citations=[]
    )
    mock_gen.return_value = mock_result

    result = audit_session({
        "what_i_practiced": "Primer intento de práctica",
        "difficulty": 1,
        "micro_error_found": "todo",
        "correction_applied": "prestar más atención",
        "hypothesis_tomorrow": "mejorar"
    }, domain="beginner", onboarding_mode=True)

    assert result.verdict.startswith("[Onboarding]")


@patch("core.auditor.generate_structured_json")
@patch("core.auditor.query_books")
def test_audit_session_rag_citations_replaced(mock_query, mock_gen):
    """Si hay RAG, las citas reales reemplazan las de la IA."""
    mock_query.return_value = [{
        "text": "La práctica deliberada requiere metas específicas",
        "book_title": "Peak",
        "chunk_index": 0
    }]
    mock_result = AuditResult(
        was_deliberate=True,
        score=90,
        confidence=0.95,
        verdict="Excelente",
        reasoning="Todo correcto",
        domain_specific_notes="N/A",
        book_citations=["Cita de IA"]
    )
    mock_gen.return_value = mock_result

    result = audit_session({
        "what_i_practiced": "Práctica deliberada avanzada",
        "difficulty": 5,
        "micro_error_found": "detalle técnico",
        "correction_applied": "ajuste fino",
        "hypothesis_tomorrow": "profundizar"
    }, domain="advanced", onboarding_mode=False)

    assert len(result.book_citations) > 0
    assert "Peak" in result.book_citations[0]
