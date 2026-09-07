"""
Direct service-layer tests for cognitive_service.

Bypasses the FastAPI HTTP layer to validate the service functions in
isolation.
"""
from datetime import datetime, timezone

import pytest

from models.cognitive_models import CognitiveSession, CognitiveSkill, CognitiveTrial
from models.models import Session as PracticeSession
from models.models import Skill
from services import cognitive_service

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(name="cog_skill")
def cog_skill_fixture(session):
    """Create a CognitiveSkill for testing."""
    skill = CognitiveSkill(
        nombre="Dual N-Back Test",
        descripcion="Test skill for cognitive service",
        fase_iq_base=115,
    )
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@pytest.fixture(name="dual_n_back_skill")
def dual_n_back_skill_fixture(session):
    """Create the standard Dual N-Back Skill row."""
    skill = Skill(
        slug="dual-n-back",
        name="Dual N-Back",
        domain="cognitive",
        skill_type="dual_n_back",
        config_path="skills/dual-n-back.yaml",
        current_level=1.0,
    )
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


# =============================================================================
# calcular_escalera_psicometrica
# =============================================================================


class TestCalcularEscaleraPsicometrica:
    """cognitive_service.calcular_escalera_psicometrica() — pure function."""

    def test_increase_on_high_precision(self):
        """Precision >= 0.80 → N+1."""
        assert cognitive_service.calcular_escalera_psicometrica(0.80, 2) == 3
        assert cognitive_service.calcular_escalera_psicometrica(0.95, 1) == 2

    def test_decrease_on_low_precision(self):
        """Precision < 0.70 and N > 1 → N-1."""
        assert cognitive_service.calcular_escalera_psicometrica(0.69, 3) == 2
        assert cognitive_service.calcular_escalera_psicometrica(0.50, 2) == 1

    def test_maintain_on_mid_precision(self):
        """Precision between 0.70 and 0.79 → N unchanged."""
        assert cognitive_service.calcular_escalera_psicometrica(0.70, 2) == 2
        assert cognitive_service.calcular_escalera_psicometrica(0.75, 3) == 3
        assert cognitive_service.calcular_escalera_psicometrica(0.79, 4) == 4

    def test_floor_at_level_one(self):
        """N=1 and precision < 0.70 → stays at 1."""
        assert cognitive_service.calcular_escalera_psicometrica(0.50, 1) == 1

    def test_never_below_one(self):
        """N=1 and precision=0 → stays at 1."""
        assert cognitive_service.calcular_escalera_psicometrica(0.0, 1) == 1

    def test_perfect_precision_at_high_n(self):
        """Perfect precision at high N."""
        assert cognitive_service.calcular_escalera_psicometrica(1.0, 10) == 11


# =============================================================================
# procesar_fin_sesion_cognitiva
# =============================================================================


class TestProcesarFinSesionCognitiva:
    """cognitive_service.procesar_fin_sesion_cognitiva() — pure function."""

    def test_empty_trials(self):
        """Empty trials returns zeros and current N."""
        result = cognitive_service.procesar_fin_sesion_cognitiva([], 3)
        assert result["precision"] == 0.0
        assert result["rt_promedio"] == 0.0
        assert result["siguiente_n"] == 3

    def test_all_correct(self):
        """All correct → precision=1.0, N+1."""
        trials = [
            CognitiveTrial(
                session_id=1, estimulo="A", respuesta_esperada="A",
                respuesta_usuario="A", es_correcto=True, tiempo_reaccion_ms=200,
            ),
            CognitiveTrial(
                session_id=1, estimulo="B", respuesta_esperada="B",
                respuesta_usuario="B", es_correcto=True, tiempo_reaccion_ms=300,
            ),
        ]
        result = cognitive_service.procesar_fin_sesion_cognitiva(trials, 2)
        assert result["precision"] == 1.0
        assert result["rt_promedio"] == 250.0
        assert result["siguiente_n"] == 3

    def test_mixed_results(self):
        """Mixed correct/incorrect → calculated precision and average RT."""
        trials = [
            CognitiveTrial(
                session_id=1, estimulo="A", respuesta_esperada="A",
                respuesta_usuario="A", es_correcto=True, tiempo_reaccion_ms=200,
            ),
            CognitiveTrial(
                session_id=1, estimulo="B", respuesta_esperada="B",
                respuesta_usuario="C", es_correcto=False, tiempo_reaccion_ms=400,
            ),
            CognitiveTrial(
                session_id=1, estimulo="C", respuesta_esperada="C",
                respuesta_usuario="C", es_correcto=True, tiempo_reaccion_ms=300,
            ),
            CognitiveTrial(
                session_id=1, estimulo="D", respuesta_esperada="D",
                respuesta_usuario="E", es_correcto=False, tiempo_reaccion_ms=500,
            ),
        ]
        result = cognitive_service.procesar_fin_sesion_cognitiva(trials, 2)
        assert result["precision"] == 0.5  # 2/4
        assert result["rt_promedio"] == 350.0
        assert result["siguiente_n"] == 1  # 0.5 < 0.7, N>1 → N-1

    def test_mid_precision_maintains_n(self):
        """Precision between 0.70 and 0.79 → maintain N."""
        trials = [
            CognitiveTrial(
                session_id=1, estimulo=f"S{i}", respuesta_esperada="A",
                respuesta_usuario="A", es_correcto=True, tiempo_reaccion_ms=300,
            )
            for i in range(7)
        ] + [
            CognitiveTrial(
                session_id=1, estimulo=f"S{i}", respuesta_esperada="A",
                respuesta_usuario="B", es_correcto=False, tiempo_reaccion_ms=300,
            )
            for i in range(3)
        ]  # 7/10 = 0.70 → maintain
        result = cognitive_service.procesar_fin_sesion_cognitiva(trials, 2)
        assert result["precision"] == 0.70
        assert result["siguiente_n"] == 2


# =============================================================================
# iniciar_sesion (cognitive)
# =============================================================================


class TestIniciarSesion:
    """cognitive_service.iniciar_sesion(db, skill_id)"""

    def test_iniciar_sesion_creates_session(self, session, cog_skill):
        """Verify cognitive session created with N=1 for first session."""
        cs = cognitive_service.iniciar_sesion(session, cog_skill.id)

        assert cs.id is not None
        assert cs.cognitive_skill_id == cog_skill.id
        assert cs.nivel_n_alcanzado == 1
        assert cs.fecha_fin is None
        assert cs.tasa_precision == 0.0
        assert cs.tiempo_reaccion_promedio_ms == 0.0
        assert cs.consolidated_session_id is None

    def test_iniciar_sesion_inherits_n_from_previous(self, session, cog_skill):
        """Second session inherits N from previous completed session."""
        # Create and complete a previous session at N=3
        past = CognitiveSession(
            cognitive_skill_id=cog_skill.id,
            nivel_n_alcanzado=3,
            tasa_precision=0.85,
            tiempo_reaccion_promedio_ms=400.0,
            fecha_fin=datetime.now(timezone.utc),
        )
        session.add(past)
        session.commit()

        cs = cognitive_service.iniciar_sesion(session, cog_skill.id)
        assert cs.nivel_n_alcanzado == 3

    def test_iniciar_sesion_ignores_unfinished_sessions(self, session, cog_skill):
        """Unfinished sessions (fecha_fin=None) should not affect N."""
        unfinished = CognitiveSession(
            cognitive_skill_id=cog_skill.id,
            nivel_n_alcanzado=5,
            tasa_precision=0.0,
            tiempo_reaccion_promedio_ms=0.0,
            fecha_fin=None,
        )
        session.add(unfinished)
        session.commit()

        cs = cognitive_service.iniciar_sesion(session, cog_skill.id)
        assert cs.nivel_n_alcanzado == 1  # No inherited from unfinished

    def test_iniciar_sesion_invalid_skill(self, session):
        """Raises ValueError for bad skill_id."""
        with pytest.raises(ValueError, match="CognitiveSkill not found"):
            cognitive_service.iniciar_sesion(session, 99999)


# =============================================================================
# finalizar_session
# =============================================================================


class TestFinalizarSession:
    """cognitive_service.finalizar_session(db, session_id)"""

    def test_finalizar_session_updates_metrics(self, session, cog_skill):
        """Finalizing a session calculates and stores metrics."""
        cs = cognitive_service.iniciar_sesion(session, cog_skill.id)

        # Add trials
        for i in range(10):
            trial = CognitiveTrial(
                session_id=cs.id,
                estimulo=f"S{i}",
                respuesta_esperada="A",
                respuesta_usuario="A" if i < 8 else "B",
                es_correcto=(i < 8),
                tiempo_reaccion_ms=200 + i * 10,
            )
            session.add(trial)
        session.commit()

        result = cognitive_service.finalizar_session(session, cs.id)

        assert result["session_id"] == cs.id
        assert result["precision"] == 0.8  # 8/10
        assert result["rt_promedio"] == 245.0  # avg of 200..290
        assert result["siguiente_n"] == 2  # 80% >= 80% → N+1

        session.refresh(cs)
        assert cs.tasa_precision == 0.8
        assert cs.fecha_fin is not None

    def test_finalizar_session_not_found(self, session):
        """Raises ValueError for bad session_id."""
        with pytest.raises(ValueError, match="Session 99999 not found"):
            cognitive_service.finalizar_session(session, 99999)


# =============================================================================
# consolidar_sesion (cognitive)
# =============================================================================


class TestConsolidarSesion:
    """cognitive_service.consolidar_sesion(db, session_id, elapsed_seconds)"""

    def test_consolidar_sesion_insufficient_trials(self, session, cog_skill, dual_n_back_skill):
        """Raises ValueError if < 10 trials."""
        cs = cognitive_service.iniciar_sesion(session, cog_skill.id)

        # Only 3 trials
        for i in range(3):
            trial = CognitiveTrial(
                session_id=cs.id,
                estimulo=f"S{i}",
                respuesta_esperada="A",
                respuesta_usuario="A",
                es_correcto=True,
                tiempo_reaccion_ms=300,
            )
            session.add(trial)
        session.commit()

        cs.fecha_fin = datetime.now(timezone.utc)
        cs.tasa_precision = 1.0
        cs.tiempo_reaccion_promedio_ms = 300.0
        session.add(cs)
        session.commit()

        with pytest.raises(ValueError, match="Minimum 10 trials required"):
            cognitive_service.consolidar_sesion(session, cs.id, elapsed_seconds=60)

    def test_consolidar_sesion_not_finalized(self, session, cog_skill, dual_n_back_skill):
        """Raises ValueError if session not finalized (fecha_fin is None)."""
        cs = cognitive_service.iniciar_sesion(session, cog_skill.id)

        with pytest.raises(ValueError, match="not finalized"):
            cognitive_service.consolidar_sesion(session, cs.id, elapsed_seconds=60)

    def test_consolidar_sesion_creates_practice_session(self, session, cog_skill, dual_n_back_skill):
        """Verify consolidation creates PracticeSession."""
        # Create session with trials and finalize it
        cs = cognitive_service.iniciar_sesion(session, cog_skill.id)

        for i in range(12):
            trial = CognitiveTrial(
                session_id=cs.id,
                estimulo=f"S{i}",
                respuesta_esperada="A",
                respuesta_usuario="A",
                es_correcto=True,
                tiempo_reaccion_ms=300,
            )
            session.add(trial)
        session.commit()
        cognitive_service.finalizar_session(session, cs.id)

        result = cognitive_service.consolidar_sesion(session, cs.id, elapsed_seconds=120)

        assert result["status"] == "consolidated"
        assert result["practice_session_id"] is not None
        assert result["cognitive_session_id"] == cs.id
        assert result["trials_count"] == 12
        assert result["n_level"] == 2  # 100% precision → N+1

        # PracticeSession exists
        ps = session.get(PracticeSession, result["practice_session_id"])
        assert ps is not None
        assert ps.skill_id == dual_n_back_skill.id
        assert "Dual N-Back" in ps.what_i_practiced

        session.refresh(cs)
        assert cs.consolidated_session_id == ps.id

    def test_consolidar_sesion_dual_n_back_skill_required(self, session, cog_skill):
        """Raises ValueError if dual_n_back Skill not seeded."""
        cs = cognitive_service.iniciar_sesion(session, cog_skill.id)

        for i in range(10):
            trial = CognitiveTrial(
                session_id=cs.id,
                estimulo=f"S{i}",
                respuesta_esperada="A",
                respuesta_usuario="A",
                es_correcto=True,
                tiempo_reaccion_ms=300,
            )
            session.add(trial)
        session.commit()
        cognitive_service.finalizar_session(session, cs.id)

        with pytest.raises(ValueError, match="Dual N-Back skill not found"):
            cognitive_service.consolidar_sesion(session, cs.id, elapsed_seconds=60)

    def test_consolidar_sesion_cognitive_session_not_found(self, session):
        """Raises ValueError for bad session_id."""
        with pytest.raises(ValueError, match="CognitiveSession not found"):
            cognitive_service.consolidar_sesion(session, 99999, elapsed_seconds=60)


# =============================================================================
# obtener_trials
# =============================================================================


class TestObtenerTrials:
    """cognitive_service.obtener_trials(db, session_id)"""

    def test_obtener_trials_returns_trials(self, session, cog_skill):
        """Returns all trials for a session."""
        cs = cognitive_service.iniciar_sesion(session, cog_skill.id)
        for i in range(5):
            trial = CognitiveTrial(
                session_id=cs.id,
                estimulo=f"S{i}",
                respuesta_esperada="A",
                respuesta_usuario="A",
                es_correcto=True,
                tiempo_reaccion_ms=200,
            )
            session.add(trial)
        session.commit()

        trials = cognitive_service.obtener_trials(session, cs.id)
        assert len(trials) == 5

    def test_obtener_trials_empty(self, session, cog_skill):
        """Returns empty list for session with no trials."""
        cs = cognitive_service.iniciar_sesion(session, cog_skill.id)
        trials = cognitive_service.obtener_trials(session, cs.id)
        assert trials == []
