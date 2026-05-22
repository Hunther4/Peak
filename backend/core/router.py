import os
import json
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

from core.settings import get_setting, set_setting
from core.model_registry import get_best_model_for_task, get_default_model
from core.ai import generate_structured_json as local_generate_structured_json
from core.utils import parse_structured_json

logger = logging.getLogger(__name__)

load_dotenv()

# Las keys se leen dinámicamente en execute_with_router para soportar hot-reload del .env

T = TypeVar('T', bound=BaseModel)

# Lazy-accessor cache for API keys.
# Each key is read from the environment on first call to its accessor and cached.
_key_cache: dict[str, str] = {}


def _get_groq_key() -> str:
    """Return GROQ_API_KEY, reading from env on first call only."""
    if "groq" not in _key_cache:
        _key_cache["groq"] = os.getenv("GROQ_API_KEY", "")
    return _key_cache["groq"]


def _get_openrouter_key() -> str:
    """Return OPENROUTER_API_KEY, reading from env on first call only."""
    if "openrouter" not in _key_cache:
        _key_cache["openrouter"] = os.getenv("OPENROUTER_API_KEY", "")
    return _key_cache["openrouter"]


def get_ai_mode() -> str:
    """Devuelve 'local' o 'api'. Por defecto 'local'."""
    return get_setting("ai_mode", "local")

def set_ai_mode(mode: str) -> None:
    if mode not in ["local", "api"]:
        mode = "local"
    set_setting("ai_mode", mode)

def _clean_and_parse_json(content: str, response_model: Type[T]) -> Optional[T]:
    return parse_structured_json(content, response_model)

def _call_groq(system_prompt: str, user_prompt: str, response_model: Type[T], model_id: str) -> Optional[T]:
    groq_api_key = _get_groq_key()
    if not groq_api_key:
        logger.warning("Groq omitido (Sin API Key)")
        return None
    
    try:
        from groq import Groq
        client = Groq(api_key=groq_api_key, timeout=30.0)
        
        schema = response_model.model_json_schema()
        augmented_system = (
            f"{system_prompt}\n\nDEBES responder ÚNICAMENTE en formato JSON válido que cumpla con este esquema:\n"
            f"{json.dumps(schema, indent=2)}\n\nNO incluyas texto fuera del JSON. NO uses markdown. Solo JSON."
        )
        
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": augmented_system},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content
        return _clean_and_parse_json(content, response_model)
    except Exception as e:
        logger.error("Groq Falló: %s: %s", type(e).__name__, e)
        return None

def _call_openrouter(system_prompt: str, user_prompt: str, response_model: Type[T], model_id: str) -> Optional[T]:
    openrouter_api_key = _get_openrouter_key()
    if not openrouter_api_key:
        logger.warning("OpenRouter omitido (Sin API Key)")
        return None
        
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
            timeout=30.0
        )
        
        schema = response_model.model_json_schema()
        augmented_system = (
            f"{system_prompt}\n\nDEBES responder ÚNICAMENTE en formato JSON válido que cumpla con este esquema:\n"
            f"{json.dumps(schema, indent=2)}\n\nNO incluyas texto fuera del JSON. NO uses markdown. Solo JSON."
        )
        
        # Opcional: headers sugeridos por OpenRouter
        extra_headers = {
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "Peak Practice"
        }
        
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": augmented_system},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            extra_headers=extra_headers
        )
        content = response.choices[0].message.content
        return _clean_and_parse_json(content, response_model)
    except Exception as e:
        logger.error("OpenRouter Falló: %s: %s", type(e).__name__, e)
        return None

def execute_with_router(task_type: str, system_prompt: str, user_prompt: str, response_model: Type[T]) -> Optional[T]:
    """Ejecuta la llamada a la IA ruteando según el modo (Local o API con fallback).

    Si hay un modelo específico seleccionado por el usuario (no auto),
    se usa ese modelo directamente en lugar del ranking inteligente.
    """
    load_dotenv()
    mode = get_ai_mode()
    
    if mode == "local":
        logger.info("Ruteando a LM Studio (Local)")
        return local_generate_structured_json(system_prompt, user_prompt, response_model, force_local=True)
    
    # Modo API
    logger.info("Ruteando a API Mode...")
    
    # Check for manual model selection
    selected_raw = get_setting("selected_model", "")
    selected = None
    if selected_raw:
        try:
            selected = json.loads(selected_raw)
        except (json.JSONDecodeError, TypeError):
            selected = None
    
    is_auto = selected is None or selected.get("auto", True)
    
    if not is_auto:
        provider = selected.get("provider")
        model_id = selected.get("model_id")
        model_name = selected.get("model_name", "")
        
        if provider == "groq" and model_id:
            logger.info("Usando modelo seleccionado: %s (Groq)", model_name)
            res = _call_groq(system_prompt, user_prompt, response_model, model_id)
            if res:
                return res
            logger.warning("Modelo seleccionado Groq falló, usando selección inteligente")
        elif provider == "openrouter" and model_id:
            logger.info("Usando modelo seleccionado: %s (OpenRouter)", model_name)
            res = _call_openrouter(system_prompt, user_prompt, response_model, model_id)
            if res:
                return res
            logger.warning("Modelo seleccionado OpenRouter falló, usando selección inteligente")
        elif provider == "lm_studio":
            logger.info("Usando modelo seleccionado: %s (Local)", model_name)
            return local_generate_structured_json(system_prompt, user_prompt, response_model, force_local=True)
    
    # Smart selection: Groq -> OpenRouter -> Local Fallback
    logger.info("Usando selección inteligente...")
    
    # 1. Intentar Groq
    groq_model = get_best_model_for_task(task_type, preferred_provider="groq")
    if groq_model and groq_model.provider == "groq":
        logger.info("Intentando Groq con %s", groq_model.name)
        res = _call_groq(system_prompt, user_prompt, response_model, groq_model.model_id)
        if res: return res
        
    # 2. Fallback OpenRouter
    or_model = get_best_model_for_task(task_type, preferred_provider="openrouter")
    if or_model and or_model.provider == "openrouter":
        logger.info("Fallback: Intentando OpenRouter con %s", or_model.name)
        res = _call_openrouter(system_prompt, user_prompt, response_model, or_model.model_id)
        if res: return res
        
    # 3. Fallback final: Local LM Studio
    logger.warning("Fallback Final: LM Studio (Local)")
    return local_generate_structured_json(system_prompt, user_prompt, response_model, force_local=True)
