import pytest
from sqlmodel import Session
from core.model_registry import get_best_model_for_task, get_default_model
from models.models import AiModel

def test_best_model_for_task_highest_score(session):
    """T-11: best_model_for_task highest score"""
    # Seed models
    model1 = AiModel(
        name="Model A", provider="groq", model_id="a", 
        capabilities="coding|general", score=80, is_active=True
    )
    model2 = AiModel(
        name="Model B", provider="groq", model_id="b", 
        capabilities="coding|general", score=90, is_active=True
    )
    model3 = AiModel(
        name="Model C", provider="openrouter", model_id="c", 
        capabilities="coding|general", score=95, is_active=True
    )
    model4 = AiModel(
        name="Model D", provider="lm_studio", model_id="d", 
        capabilities="general", score=70, is_active=True
    )
    default_model = AiModel(
        name="Default Local", provider="lm_studio", model_id="local-model", 
        capabilities="general", score=50, is_active=True
    )
    session.add_all([model1, model2, model3, model4, default_model])
    session.commit()

    # Task 'coding', preferred provider 'groq'. 
    # Models A (80) and B (90) have coding and are groq. Should return B.
    best = get_best_model_for_task("coding", preferred_provider="groq")
    assert best.name == "Model B"
    assert best.score == 90

    # Task 'coding', no preferred provider.
    # Model C has the highest score (95) among all coding models.
    best_overall = get_best_model_for_task("coding")
    assert best_overall.name == "Model C"
    assert best_overall.score == 95

def test_invalid_provider_returns_default(session):
    """T-12: invalid provider returns default"""
    # Seed the default model
    default_model = AiModel(
        name="Default Local", provider="lm_studio", model_id="local-model", 
        capabilities="general", score=50, is_active=True
    )
    session.add(default_model)
    session.commit()

    # Use a provider that doesn't exist
    best = get_best_model_for_task("coding", preferred_provider="invalid_provider")
    
    # Should return the default model
    default = get_default_model()
    assert best.model_id == default.model_id

