"""
Tests para core/mental.py

Generación de representaciones mentales y desafíos.
"""
import pytest
from unittest.mock import patch, MagicMock
from core.mental import (
    generate_mental_rep,
    generate_challenge,
    generate_challenge_from_assessment,
    MentalRepResult,
    ChallengeResult,
)


# --- generate_mental_rep ---

@patch("core.mental.query_books")
@patch("core.mental.generate_structured_json")
def test_generate_mental_rep_first_version(mock_gen, mock_query):
    """Primera representación mental (sin previa) genera v1."""
    mock_query.return_value = []
    mock_result = MentalRepResult(
        description="Veo el piano como coordinación rítmica",
        is_real_shift=True,
        reasoning="Primera conceptualización",
        key_insight="La práctica requiere atención deliberada"
    )
    mock_gen.return_value = mock_result

    result = generate_mental_rep(
        skill_name="Piano",
        domain="music",
        skill_type="staircase",
        current_level=10.0,
        prev_description=None,
        prev_version=0,
        session_summary="3 sesiones de práctica básica"
    )

    assert result is not None
    assert result.is_real_shift is True
    mock_gen.assert_called_once()
    # Verificar que task_type="assessment" se pasa
    call_kwargs = mock_gen.call_args
    assert call_kwargs.kwargs.get("task_type") == "assessment"


@patch("core.mental.query_books")
@patch("core.mental.generate_structured_json")
def test_generate_mental_rep_with_previous(mock_gen, mock_query):
    """Con representación previa, compara para determinar si hay shift real."""
    mock_query.return_value = []
    mock_result = MentalRepResult(
        description="Antes veía escalas como dedos, ahora veo como patrones armónicos",
        is_real_shift=True,
        reasoning="Cambio de perspectiva de técnica a armonía",
        key_insight="Las escalas son progresiones"
    )
    mock_gen.return_value = mock_result

    result = generate_mental_rep(
        skill_name="Guitarra",
        domain="music",
        skill_type="staircase",
        current_level=40.0,
        prev_description="Las escalas son secuencias de dedos",
        prev_version=3,
        session_summary="10 sesiones de práctica de escalas"
    )

    assert result is not None
    assert result.is_real_shift is True


@patch("core.mental.query_books")
@patch("core.mental.generate_structured_json")
def test_generate_mental_rep_ai_fails(mock_gen, mock_query):
    """Cuando la IA falla, retorna None."""
    mock_query.return_value = []
    mock_gen.return_value = None

    result = generate_mental_rep(
        skill_name="Test",
        domain="test",
        skill_type="problem_set",
        current_level=1.0,
        prev_description=None,
        prev_version=0,
        session_summary="Sin sesiones"
    )

    assert result is None


@patch("core.mental.query_books")
@patch("core.mental.generate_structured_json")
def test_generate_mental_rep_with_rag(mock_gen, mock_query):
    """Si hay libros indexados, el prompt incluye contexto RAG."""
    mock_query.return_value = [{
        "text": "Las representaciones mentales son la clave de la práctica deliberada",
        "book_title": "Peak",
        "chunk_index": 5
    }]
    mock_result = MentalRepResult(
        description="Test",
        is_real_shift=True,
        reasoning="Test",
        key_insight="Test"
    )
    mock_gen.return_value = mock_result

    generate_mental_rep(
        skill_name="Piano",
        domain="music",
        skill_type="staircase",
        current_level=20.0,
        prev_description=None,
        prev_version=0,
        session_summary="Sesión 1"
    )

    mock_query.assert_called_once()
    mock_gen.assert_called_once()


# --- generate_challenge ---

@patch("core.mental.query_books")
@patch("core.mental.generate_structured_json")
def test_generate_challenge_beginner(mock_gen, mock_query):
    """Nivel bajo sugiere dificultad 2-3."""
    mock_query.return_value = []
    mock_result = ChallengeResult(
        description="Practicar compás 1-4 a 60bpm",
        difficulty_target=2,
        rationale="Nivel principiante requiere enfoque básico"
    )
    mock_gen.return_value = mock_result

    result = generate_challenge(
        skill_name="Piano",
        domain="music",
        skill_type="staircase",
        current_level=15.0,
        last_session="qué: escalas, dificultad: 2, error: tempo irregular",
        difficulty_override=None
    )

    assert result is not None
    assert result.difficulty_target == 2
    mock_gen.assert_called_once()
    call_kwargs = mock_gen.call_args
    assert call_kwargs.kwargs.get("task_type") == "reasoning"


@patch("core.mental.query_books")
@patch("core.mental.generate_structured_json")
def test_generate_challenge_intermediate(mock_gen, mock_query):
    """Nivel medio sugiere dificultad 3-4."""
    mock_query.return_value = []
    mock_result = ChallengeResult(
        description="Practicar transiciones rápidas a 90bpm",
        difficulty_target=3,
        rationale="Nivel intermedio puede manejar más complejidad"
    )
    mock_gen.return_value = mock_result

    result = generate_challenge(
        skill_name="Guitarra",
        domain="music",
        skill_type="staircase",
        current_level=45.0,
        last_session="qué: arpegios, error: dedos cruzados",
        difficulty_override=None
    )

    assert result is not None
    assert result.difficulty_target == 3


@patch("core.mental.query_books")
@patch("core.mental.generate_structured_json")
def test_generate_challenge_advanced(mock_gen, mock_query):
    """Nivel alto sugiere dificultad 4-5."""
    mock_query.return_value = []
    mock_result = ChallengeResult(
        description="Ejecutar pieza completa a tempo original",
        difficulty_target=5,
        rationale="Nivel avanzado listo para desafío máximo"
    )
    mock_gen.return_value = mock_result

    result = generate_challenge(
        skill_name="Violín",
        domain="music",
        skill_type="staircase",
        current_level=75.0,
        last_session="qué: conciertos, error: ninguno significativo",
        difficulty_override=None
    )

    assert result is not None
    assert result.difficulty_target == 5


@patch("core.mental.query_books")
@patch("core.mental.generate_structured_json")
def test_generate_challenge_with_override(mock_gen, mock_query):
    """difficulty_override reemplaza el cálculo automático."""
    mock_query.return_value = []
    mock_result = ChallengeResult(
        description="Desafío personalizado",
        difficulty_target=4,
        rationale="Override del usuario"
    )
    mock_gen.return_value = mock_result

    result = generate_challenge(
        skill_name="Test",
        domain="test",
        skill_type="problem_set",
        current_level=10.0,
        last_session="test session",
        difficulty_override=4
    )

    assert result is not None
    assert result.difficulty_target == 4


@patch("core.mental.query_books")
@patch("core.mental.generate_structured_json")
def test_generate_challenge_with_rag(mock_gen, mock_query):
    """Si hay libros, la descripción del challenge incluye la fuente."""
    mock_query.return_value = [{
        "text": "Practicar con foco en la calidad del movimiento",
        "book_title": "Peak",
        "chunk_index": 10
    }]
    mock_result = ChallengeResult(
        description="Practicar movimientos lentos",
        difficulty_target=3,
        rationale="Basado en libro"
    )
    mock_gen.return_value = mock_result

    result = generate_challenge(
        skill_name="Piano",
        domain="music",
        skill_type="staircase",
        current_level=30.0,
        last_session="test",
        difficulty_override=None
    )

    assert result is not None
    assert result.description.startswith("[Peak]")


@patch("core.mental.query_books")
@patch("core.mental.generate_structured_json")
def test_generate_challenge_ai_fails(mock_gen, mock_query):
    """Cuando la IA falla, retorna None."""
    mock_query.return_value = []
    mock_gen.return_value = None

    result = generate_challenge(
        skill_name="Test",
        domain="test",
        skill_type="problem_set",
        current_level=10.0,
        last_session="test",
        difficulty_override=None
    )

    assert result is None


# --- generate_challenge_from_assessment ---

@patch("core.mental.generate_challenge")
def test_challenge_from_assessment_calls_generate(mock_gen):
    """generate_challenge_from_assessment delega a generate_challenge."""
    mock_result = ChallengeResult(
        description="Desafío post-assessment",
        difficulty_target=3,
        rationale="Basado en score bajo"
    )
    mock_gen.return_value = mock_result

    result = generate_challenge_from_assessment(
        skill_name="Piano",
        domain="music",
        skill_type="staircase",
        current_level=25.0,
        assessment_score=40.0,
        assessment_type="skill_audit",
        assessment_notes="Falta precisión en el tempo"
    )

    assert result is not None
    mock_gen.assert_called_once()
    call_args = mock_gen.call_args
    assert call_args.kwargs["skill_name"] == "Piano"
    assert "Assessment skill_audit" in call_args.kwargs["last_session"]
