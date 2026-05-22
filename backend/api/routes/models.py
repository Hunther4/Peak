from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, Literal

from core.model_registry import get_available_models, get_best_model_for_task
from core.router import get_ai_mode, set_ai_mode
from core.limiter import limiter, get_rate_limit_str

router = APIRouter()

class ModeUpdateRequest(BaseModel):
    mode: Literal["local", "api"]

@router.get("/")
def get_models():
    """Retorna lista de modelos activos."""
    return get_available_models()

@router.get("/available")
def get_available_for_task(task: Optional[str] = None):
    """Retorna los modelos disponibles para una tarea específica."""
    models = get_available_models()
    if not task:
        return models
    return [m for m in models if m.capabilities and task in m.capabilities.split("|")]

@router.get("/status")
def get_mode_status():
    """Retorna el modo actual (local o api)."""
    return {"mode": get_ai_mode()}

@router.put("/mode")
@limiter.limit(get_rate_limit_str())
def update_mode(request: Request, req: ModeUpdateRequest):
    """Cambia el modo de operación de la IA."""
    set_ai_mode(req.mode)
    return {"status": "success", "mode": req.mode}

@router.get("/best")
def get_best_model(task: str):
    """Retorna el mejor modelo para la tarea según el router."""
    mode = get_ai_mode()
    if mode == "local":
        return get_best_model_for_task(task, preferred_provider="lm_studio")
    
    # Simular ruteo: Groq -> OpenRouter -> Local
    best_groq = get_best_model_for_task(task, preferred_provider="groq")
    if best_groq and best_groq.provider == "groq":
        return best_groq
        
    best_or = get_best_model_for_task(task, preferred_provider="openrouter")
    if best_or and best_or.provider == "openrouter":
        return best_or
        
    return get_best_model_for_task(task, preferred_provider="lm_studio")
