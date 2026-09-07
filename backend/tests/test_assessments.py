"""
Tests de assessments (T-05, T-06).

Validan:
- Assessment formal actualiza current_level del skill
- Tipo inválido es rechazado
"""


class TestCreateAssessment:
    """CRUD de assessments con side effects en Skill."""

    # T-05: Assessment formal alimenta la escalera (no sobreescribe)
    def test_formal_assessment_feeds_staircase(self, client, skill_factory, session):
        """Un assessment formal debe alimentar la escalera, no sobreescribir el level directamente."""
        from sqlmodel import select

        from models.models import SkillLevelHistory

        seed_skill = skill_factory(level=25.0)
        assert seed_skill.current_level == 25.0

        response = client.post("/api/assessments/", json={
            "skill_id": seed_skill.id,
            "type": "formal",
            "score": 72.5,
            "notes": "Evaluación formal de memoria con 15 dígitos",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 72.5
        assert data["type"] == "formal"

        # Verificar que el skill NO se sobreescribió — la escalera solo registra
        skill_response = client.get(f"/api/skills/{seed_skill.id}")
        assert skill_response.status_code == 200
        assert skill_response.json()["current_level"] == 25.0  # No cambia con 1 sola evaluación

        # Verificar que se creó un registro en SkillLevelHistory
        history = session.exec(
            select(SkillLevelHistory).where(SkillLevelHistory.skill_id == seed_skill.id)
        ).all()
        assert len(history) == 1
        assert history[0].success is True  # 72.5 >= 60%

    # T-06: Tipo inválido → 422 (Pydantic Literal validation)
    def test_assessment_invalid_type_returns_422(self, client, skill_factory):
        """Solo 'probe' y 'formal' son tipos válidos — Pydantic Literal valida."""
        seed_skill = skill_factory()
        response = client.post("/api/assessments/", json={
            "skill_id": seed_skill.id,
            "type": "invalid_type",
            "score": 50.0,
        })

        assert response.status_code == 422

    def test_probe_assessment_does_not_update_level(self, client, skill_factory):
        """Un assessment tipo probe NO debe modificar el current_level."""
        seed_skill = skill_factory()
        original_level = seed_skill.current_level

        response = client.post("/api/assessments/", json={
            "skill_id": seed_skill.id,
            "type": "probe",
            "score": 90.0,
            "notes": "Prueba rápida",
        })

        assert response.status_code == 201

        skill_response = client.get(f"/api/skills/{seed_skill.id}")
        assert skill_response.json()["current_level"] == original_level

    def test_assessment_score_below_zero_returns_422(self, client, skill_factory):
        """Score < 0 debe ser rechazado por Field(ge=0)."""
        seed_skill = skill_factory()
        response = client.post("/api/assessments/", json={
            "skill_id": seed_skill.id,
            "type": "probe",
            "score": -5.0,
        })
        assert response.status_code == 422

    def test_assessment_score_above_100_returns_422(self, client, skill_factory):
        """Score > 100 debe ser rechazado por Field(le=100)."""
        seed_skill = skill_factory()
        response = client.post("/api/assessments/", json={
            "skill_id": seed_skill.id,
            "type": "probe",
            "score": 150.0,
        })
        assert response.status_code == 422
