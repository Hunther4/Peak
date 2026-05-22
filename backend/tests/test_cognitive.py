import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from services.cognitive_service import calcular_escalera_psicometrica
from models.cognitive_models import CognitiveSkill, CognitiveSession, CognitiveTrial


# ============================================================================
# 1. PRUEBAS UNITARIAS: Algoritmo de Escalera Psicométrica (Jaeggi et al.)
# ============================================================================

def test_ladder_logic_increase():
    """GIVEN precision >= 80% WHEN calculating next N THEN N increases by 1."""
    assert calcular_escalera_psicometrica(0.80, 2) == 3
    assert calcular_escalera_psicometrica(0.95, 1) == 2


def test_ladder_logic_decrease():
    """GIVEN precision < 70% WHEN calculating next N THEN N decreases by 1."""
    assert calcular_escalera_psicometrica(0.69, 3) == 2
    assert calcular_escalera_psicometrica(0.50, 2) == 1


def test_ladder_logic_maintain():
    """GIVEN precision between 70% and 79% WHEN calculating next N THEN N remains identical."""
    assert calcular_escalera_psicometrica(0.70, 2) == 2
    assert calcular_escalera_psicometrica(0.75, 3) == 3
    assert calcular_escalera_psicometrica(0.79, 4) == 4


def test_ladder_logic_floor():
    """GIVEN N is 1 and precision < 70% WHEN calculating next N THEN N stays 1 (floor boundary)."""
    assert calcular_escalera_psicometrica(0.50, 1) == 1


# ============================================================================
# 2. PRUEBAS DE INTEGRACIÓN: Endpoints FastAPI (/api/cognitive)
# ============================================================================

@pytest.fixture(name="cog_skill")
def cog_skill_fixture(session):
    """Fixture que crea un CognitiveSkill base."""
    skill = CognitiveSkill(
        nombre="N-Back Aritmético",
        descripcion="Entrenamiento científico de memoria de trabajo",
        fase_iq_base=115
    )
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


def test_create_cognitive_skill(client):
    """POST /api/cognitive/skills/ crea una nueva habilidad cognitiva."""
    payload = {
        "nombre": "Dual N-Back Auditivo",
        "descripcion": "Estímulos de audio adaptativos",
        "fase_iq_base": 130
    }
    resp = client.post("/api/cognitive/skills/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["nombre"] == "Dual N-Back Auditivo"
    assert data["fase_iq_base"] == 130
    assert data["id"] is not None


def test_create_cognitive_skill_duplicate(client, cog_skill):
    """POST habilidad con nombre duplicado retorna 400."""
    payload = {
        "nombre": cog_skill.nombre,
        "descripcion": "Otra descripcion",
        "fase_iq_base": 100
    }
    resp = client.post("/api/cognitive/skills/", json=payload)
    assert resp.status_code == 400
    assert "Ya existe" in resp.json()["detail"]


def test_get_cognitive_skills(client, cog_skill):
    """GET /api/cognitive/skills/ devuelve la lista de habilidades cognitivas."""
    resp = client.get("/api/cognitive/skills/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["nombre"] == cog_skill.nombre


def test_start_cognitive_session(client, cog_skill):
    """POST /api/cognitive/sessions/ inicia sesión con N=1 por defecto."""
    payload = {"cognitive_skill_id": cog_skill.id}
    resp = client.post("/api/cognitive/sessions/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["cognitive_skill_id"] == cog_skill.id
    assert data["nivel_n_alcanzado"] == 1
    assert data["fecha_fin"] is None


def test_start_cognitive_session_not_found(client):
    """POST /api/cognitive/sessions/ con ID inexistente retorna 404."""
    resp = client.post("/api/cognitive/sessions/", json={"cognitive_skill_id": 9999})
    assert resp.status_code == 404


def test_upload_trials_bulk_and_finalize(client, cog_skill):
    """Flujo completo de sesión: Iniciar -> Bulk POST Trials -> Finalizar (Sube de N)."""
    # 1. Iniciar sesión
    session_resp = client.post("/api/cognitive/sessions/", json={"cognitive_skill_id": cog_skill.id})
    assert session_resp.status_code == 201
    session_id = session_resp.json()["id"]

    # 2. Bulk Upload Trials (Precisión = 100%, Tiempo reacción promedio = 350ms)
    trials_payload = {
        "session_id": session_id,
        "trials": [
            {"estimulo": "A", "respuesta_esperada": "Match", "respuesta_usuario": "Match", "es_correcto": True, "tiempo_reaccion_ms": 300},
            {"estimulo": "B", "respuesta_esperada": "NoMatch", "respuesta_usuario": "NoMatch", "es_correcto": True, "tiempo_reaccion_ms": 400},
        ]
    }
    trials_resp = client.post("/api/cognitive/trials/", json=trials_payload)
    assert trials_resp.status_code == 201
    assert trials_resp.json()["count"] == 2

    # 3. Finalizar Sesión
    finalize_resp = client.post(f"/api/cognitive/sessions/{session_id}/finalize/")
    assert finalize_resp.status_code == 200
    metrics = finalize_resp.json()
    assert metrics["session_id"] == session_id
    assert metrics["precision"] == 1.0
    assert metrics["rt_promedio"] == 350.0
    assert metrics["siguiente_n"] == 2  # Subió a N=2 (Jaeggi Escalera)


def test_session_adaptive_ladder_continuation(client, cog_skill, session):
    """Una nueva sesión hereda el nivel N de la sesión anterior completada para esa skill."""
    # Creamos una sesión completada en nivel N=3
    past_session = CognitiveSession(
        cognitive_skill_id=cog_skill.id,
        nivel_n_alcanzado=3,
        tasa_precision=0.85,
        tiempo_reaccion_promedio_ms=400.0,
        fecha_fin=None # se finalizará a través de la API o directo
    )
    session.add(past_session)
    session.commit()
    session.refresh(past_session)

    # Añadimos un trial para poder finalizarla
    trial = CognitiveTrial(
        session_id=past_session.id,
        estimulo="C",
        respuesta_esperada="A",
        respuesta_usuario="A",
        es_correcto=True,
        tiempo_reaccion_ms=250
    )
    session.add(trial)
    session.commit()

    # Finalizamos la sesión via API para setear fecha_fin y confirmar N=4
    finalize_resp = client.post(f"/api/cognitive/sessions/{past_session.id}/finalize/")
    assert finalize_resp.status_code == 200
    assert finalize_resp.json()["siguiente_n"] == 4

    # Iniciamos una nueva sesión, y debe continuar en N=4
    new_resp = client.post("/api/cognitive/sessions/", json={"cognitive_skill_id": cog_skill.id})
    assert new_resp.status_code == 201
    assert new_resp.json()["nivel_n_alcanzado"] == 4


def test_trials_blocked_on_finalized_session(client, cog_skill):
    """No se pueden subir trials a una sesión que ya ha sido finalizada."""
    # 1. Iniciar y finalizar inmediatamente
    session_resp = client.post("/api/cognitive/sessions/", json={"cognitive_skill_id": cog_skill.id})
    session_id = session_resp.json()["id"]
    client.post(f"/api/cognitive/sessions/{session_id}/finalize/")

    # 2. Intentar subir trials
    trials_payload = {
        "session_id": session_id,
        "trials": [
            {"estimulo": "A", "respuesta_esperada": "B", "respuesta_usuario": "B", "es_correcto": True, "tiempo_reaccion_ms": 300}
        ]
    }
    resp = client.post("/api/cognitive/trials/", json=trials_payload)
    assert resp.status_code == 400
    assert "ya finalizada" in resp.json()["detail"]


# ============================================================================
# 3. SEGURIDAD: Autenticación en Endpoints de Telemetría Cognitiva
# ============================================================================

class TestCognitiveAuth:
    """Verificación de que el middleware de API Key protege las nuevas rutas de Cognitive."""

    @pytest.fixture(autouse=True)
    def enable_auth(self, monkeypatch):
        """Habilitamos la seguridad para esta sección eliminando DISABLE_AUTH."""
        monkeypatch.delenv("DISABLE_AUTH", raising=False)

    def test_cognitive_endpoints_return_401_without_key(self, client):
        """GIVEN X-API-Key omitido WHEN cualquier endpoint cognitivo THEN 401."""
        endpoints = [
            ("/api/cognitive/skills/", "GET"),
            ("/api/cognitive/skills/", "POST"),
            ("/api/cognitive/sessions/", "POST"),
            ("/api/cognitive/trials/", "POST"),
            ("/api/cognitive/sessions/1/finalize/", "POST"),
        ]
        for path, method in endpoints:
            if method == "GET":
                resp = client.get(path)
            else:
                resp = client.post(path, json={})
            assert resp.status_code == 401, f"{method} {path} debió ser bloqueada con 401."

    def test_cognitive_endpoints_work_with_valid_key(self, client, auth_headers):
        """GIVEN X-API-Key correcto WHEN GET skills THEN 200."""
        resp = client.get("/api/cognitive/skills/", headers=auth_headers)
        assert resp.status_code == 200
