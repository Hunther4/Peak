import os
import json
import logging
from openai import OpenAI
from pydantic import BaseModel
from typing import Type, TypeVar, Optional

from core.utils import parse_structured_json, sanitize_prompt

logger = logging.getLogger(__name__)

# Lazy client — not initialized at import time.
# First call to get_client() reads env vars and caches the instance.
_client: Optional[OpenAI] = None

T = TypeVar('T', bound=BaseModel)


def get_client() -> OpenAI:
    """Return the OpenAI client, creating it lazily on first call.

    Reads LM_STUDIO_API_KEY, LM_STUDIO_BASE_URL, and LM_STUDIO_TIMEOUT
    from the environment on first invocation; caches the instance thereafter.
    """
    global _client
    if _client is None:
        base_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
        api_key = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
        timeout_str = os.getenv("LM_STUDIO_TIMEOUT", "60")
        try:
            timeout = int(timeout_str)
        except (ValueError, TypeError):
            timeout = 60
        _client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)
    return _client


# Backward-compatible module-level attribute for existing code and mock patches.
# "core.ai.client" resolves to the lazy getter via __getattr__.
# This __getattr__ is only called on attribute access, NOT at import time.
def __getattr__(name):
    if name == "client":
        return get_client()
    raise AttributeError(f"module 'core.ai' has no attribute '{name}'")


class QuickLogCompletion(BaseModel):
    correction_applied: str
    hypothesis_tomorrow: str


def generate_structured_json(system_prompt: str, user_prompt: str, response_model: Type[T], max_retries: int = 1, force_local: bool = False, task_type: str = "audit") -> Optional[T]:
    """
    Llama a la IA pidiendo JSON estructurado.
    Si force_local=True, saltea el router y ejecuta directo en LM Studio.
    Si force_local=False (default), delega al router si ai_mode == "api".
    task_type permite propagar la capability al router (e.g., "audit", "assessment", "reasoning").

    force_local es usado por el router para evitar recursión infinita
    cuando todos los providers API fallan y se cae a local.
    """
    if not force_local:
        from core.router import get_ai_mode
        if get_ai_mode() == "api":
            from core.router import execute_with_router
            return execute_with_router(task_type, system_prompt, user_prompt, response_model)

    for attempt in range(max_retries + 1):
        try:
            schema = response_model.model_json_schema()
            augmented_system = (
                f"{system_prompt}\n\n"
                f"DEBES responder ÚNICAMENTE en formato JSON válido que cumpla con este esquema:\n"
                f"{json.dumps(schema, indent=2)}\n\n"
                f"NO incluyas texto fuera del JSON. NO uses markdown. Solo JSON."
            )

            client = get_client()
            response = client.chat.completions.create(
                model="local-model",  # LM Studio ignora el nombre del modelo
                messages=[
                    {"role": "system", "content": augmented_system},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
            )

            if not response.choices:
                logger.warning("Intento %d: choices vacío", attempt + 1)
                continue

            content = response.choices[0].message.content
            if not content:
                logger.warning("Intento %d: respuesta vacía", attempt + 1)
                continue

            parsed = parse_structured_json(content, response_model)
            if parsed:
                return parsed

        except Exception as e:
            logger.error("Error en intento %d: %s: %s", attempt + 1, type(e).__name__, e)
            if attempt == max_retries:
                return None
    return None


def generate_quick_log_completions(what_i_practiced: str, micro_error_found: str, domain: str) -> dict:
    """
    Genera `correction_applied` y `hypothesis_tomorrow` para el modo Quick Log.
    Delega al router en background.
    """
    system_prompt = (
        f"Eres un coach de práctica deliberada para el dominio: {domain}.\n"
        f"El usuario está usando el 'Quick Log' y está fatigado tras su sesión. "
        f"Ha provisto el objetivo de la sesión y el micro-error encontrado.\n\n"
        f"Tu tarea es DEDUCIR lógicamente:\n"
        f"1. Qué corrección probablemente aplicó (correction_applied).\n"
        f"2. Cuál debería ser la hipótesis para la próxima sesión (hypothesis_tomorrow).\n\n"
        f"Mantén el tono directo, sin adornos. Sé conciso y asertivo."
    )

    user_prompt = (
        f"Qué practiqué: {sanitize_prompt(what_i_practiced)}\n"
        f"Error detectado: {sanitize_prompt(micro_error_found)}\n\n"
        f"Completá los campos."
    )

    from core.router import get_ai_mode
    if get_ai_mode() == "api":
        from core.router import execute_with_router
        result = execute_with_router("quick_log", system_prompt, user_prompt, QuickLogCompletion)
    else:
        result = generate_structured_json(system_prompt, user_prompt, QuickLogCompletion, task_type="quick_log")

    if result:
        return result.model_dump()
    return {
        "correction_applied": "No se pudo autogenerar — LM Studio/Router no respondió.",
        "hypothesis_tomorrow": "Revisar sesión manualmente en la UI."
    }
