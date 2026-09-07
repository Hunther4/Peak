import sys
from pathlib import Path

# Asegurar path correcto
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select

from core.database import engine
from models.models import AiModel

GROQ_MODELS = [
    {
        "name": "Llama 3.1 8B", "provider": "groq", "model_id": "llama-3.1-8b-instant",
        "score": 95, "strengths": "Rápido|Suficiente|131K context",
        "weaknesses": "Menos preciso en tareas complejas", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "Llama 3.3 70B", "provider": "groq", "model_id": "llama-3.3-70b-versatile",
        "score": 93, "strengths": "Razonamiento profundo|Código|131K context",
        "weaknesses": "Más lento que 8B", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "Llama 4 Scout 17B", "provider": "groq", "model_id": "meta-llama/llama-4-scout-17b-16e-instruct",
        "score": 91, "strengths": "Llama 4|MoE|131K context",
        "weaknesses": "Nuevo, menos testado", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "Qwen3 32B", "provider": "groq", "model_id": "qwen/qwen3-32b",
        "score": 90, "strengths": "32B params|131K context|Multilingüe",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "GPT-OSS 120B", "provider": "groq", "model_id": "openai/gpt-oss-120b",
        "score": 88, "strengths": "120B params|OpenAI open source|131K context",
        "weaknesses": "Lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "GPT-OSS 20B", "provider": "groq", "model_id": "openai/gpt-oss-20b",
        "score": 82, "strengths": "OpenAI open source|131K context",
        "weaknesses": "Menos capaz", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
]

OPENROUTER_MODELS = [
    {
        "name": "Qwen3 Coder", "provider": "openrouter", "model_id": "qwen/qwen3-coder:free",
        "score": 87, "strengths": "1M context|Código|Gratis",
        "weaknesses": "Lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 1048576
    },
    {
        "name": "Nemotron 3 Super 120B", "provider": "openrouter", "model_id": "nvidia/nemotron-3-super-120b-a12b:free",
        "score": 86, "strengths": "120B params|1M context|Gratis",
        "weaknesses": "Lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 1000000
    },
    {
        "name": "Hermes 3 405B", "provider": "openrouter", "model_id": "nousresearch/hermes-3-llama-3.1-405b:free",
        "score": 85, "strengths": "405B params|Razonamiento|Gratis",
        "weaknesses": "Muy lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "GPT-OSS 120B (OR)", "provider": "openrouter", "model_id": "openai/gpt-oss-120b:free",
        "score": 84, "strengths": "120B params|OpenAI open source|Gratis",
        "weaknesses": "Lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "Kimi K2.6", "provider": "openrouter", "model_id": "moonshotai/kimi-k2.6:free",
        "score": 83, "strengths": "262K context|Multimodal|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 262144
    },
    {
        "name": "Gemma 4 31B", "provider": "openrouter", "model_id": "google/gemma-4-31b-it:free",
        "score": 81, "strengths": "Google|262K context|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 262144
    },
    {
        "name": "Qwen3 Next 80B", "provider": "openrouter", "model_id": "qwen/qwen3-next-80b-a3b-instruct:free",
        "score": 80, "strengths": "80B params|262K context|Gratis",
        "weaknesses": "Lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 262144
    },
    {
        "name": "Llama 3.3 70B (OR)", "provider": "openrouter", "model_id": "meta-llama/llama-3.3-70b-instruct:free",
        "score": 79, "strengths": "Llama 3.3|131K context|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "Gemma 4 26B", "provider": "openrouter", "model_id": "google/gemma-4-26b-a4b-it:free",
        "score": 78, "strengths": "Google|262K context|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 262144
    },
    {
        "name": "Nemotron 3 Nano 30B", "provider": "openrouter", "model_id": "nvidia/nemotron-3-nano-30b-a3b:free",
        "score": 77, "strengths": "30B params|256K context|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 256000
    },
    {
        "name": "Nemotron Nano 12B VL", "provider": "openrouter", "model_id": "nvidia/nemotron-nano-12b-v2-vl:free",
        "score": 76, "strengths": "Vision|128K context|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 128000
    },
    {
        "name": "Nemotron Nano 9B", "provider": "openrouter", "model_id": "nvidia/nemotron-nano-9b-v2:free",
        "score": 75, "strengths": "Rápido|128K context|Gratis",
        "weaknesses": "Menos preciso", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 128000
    },
    {
        "name": "GPT-OSS 20B (OR)", "provider": "openrouter", "model_id": "openai/gpt-oss-20b:free",
        "score": 74, "strengths": "OpenAI open source|131K context|Gratis",
        "weaknesses": "Menos capaz", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "GLM 4.5 Air", "provider": "openrouter", "model_id": "z-ai/glm-4.5-air:free",
        "score": 73, "strengths": "131K context|Gratis",
        "weaknesses": "Desconocido", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "Laguna M", "provider": "openrouter", "model_id": "poolside/laguna-m.1:free",
        "score": 72, "strengths": "262K context|Gratis",
        "weaknesses": "Desconocido", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 262144
    },
    {
        "name": "Llama 3.2 3B (OR)", "provider": "openrouter", "model_id": "meta-llama/llama-3.2-3b-instruct:free",
        "score": 65, "strengths": "Rápido|131K context|Gratis",
        "weaknesses": "Solo 3B params", "capabilities": "math_problem|iq_puzzle|memory_game|quick_log|general",
        "context_window": 131072
    },
]

LM_STUDIO_MODEL = [
    {
        "name": "Local (LM Studio)", "provider": "lm_studio", "model_id": "local-model",
        "score": 70, "strengths": "Privado|Sin límites|Sin API key|50K context",
        "weaknesses": "Depende del modelo descargado|Más lento sin GPU",
        "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 50000
    }
]

OPENROUTER_MODELS = [
    {
        "name": "Qwen3 Coder", "provider": "openrouter", "model_id": "qwen/qwen3-coder:free",
        "score": 88, "strengths": "1M context|Código|Gratis",
        "weaknesses": "Lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 1048576
    },
    {
        "name": "Nemotron 3 Super 120B", "provider": "openrouter", "model_id": "nvidia/nemotron-3-super-120b-a12b:free",
        "score": 87, "strengths": "120B params|1M context|Gratis",
        "weaknesses": "Lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 1000000
    },
    {
        "name": "Hermes 3 405B", "provider": "openrouter", "model_id": "nousresearch/hermes-3-llama-3.1-405b:free",
        "score": 86, "strengths": "405B params|Razonamiento|Gratis",
        "weaknesses": "Muy lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "GPT-OSS 120B", "provider": "openrouter", "model_id": "openai/gpt-oss-120b:free",
        "score": 84, "strengths": "120B params|OpenAI open source|Gratis",
        "weaknesses": "Lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "Kimi K2.6", "provider": "openrouter", "model_id": "moonshotai/kimi-k2.6:free",
        "score": 83, "strengths": "262K context|Multimodal|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 262144
    },
    {
        "name": "Gemma 4 31B", "provider": "openrouter", "model_id": "google/gemma-4-31b-it:free",
        "score": 82, "strengths": "Google|262K context|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 262144
    },
    {
        "name": "Qwen3 Next 80B", "provider": "openrouter", "model_id": "qwen/qwen3-next-80b-a3b-instruct:free",
        "score": 81, "strengths": "80B params|262K context|Gratis",
        "weaknesses": "Lento", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 262144
    },
    {
        "name": "Llama 3.3 70B (OR)", "provider": "openrouter", "model_id": "meta-llama/llama-3.3-70b-instruct:free",
        "score": 80, "strengths": "Llama 3.3|131K context|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "Gemma 4 26B", "provider": "openrouter", "model_id": "google/gemma-4-26b-a4b-it:free",
        "score": 78, "strengths": "Google|262K context|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 262144
    },
    {
        "name": "Nemotron 3 Nano 30B", "provider": "openrouter", "model_id": "nvidia/nemotron-3-nano-30b-a3b:free",
        "score": 76, "strengths": "30B params|256K context|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 256000
    },
    {
        "name": "Nemotron Nano 12B VL", "provider": "openrouter", "model_id": "nvidia/nemotron-nano-12b-v2-vl:free",
        "score": 74, "strengths": "Vision|128K context|Gratis",
        "weaknesses": "Rate limit", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 128000
    },
    {
        "name": "Nemotron Nano 9B", "provider": "openrouter", "model_id": "nvidia/nemotron-nano-9b-v2:free",
        "score": 72, "strengths": "Rápido|128K context|Gratis",
        "weaknesses": "Menos preciso", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 128000
    },
    {
        "name": "GPT-OSS 20B", "provider": "openrouter", "model_id": "openai/gpt-oss-20b:free",
        "score": 70, "strengths": "OpenAI open source|131K context|Gratis",
        "weaknesses": "Menos capaz", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "GLM 4.5 Air", "provider": "openrouter", "model_id": "z-ai/glm-4.5-air:free",
        "score": 68, "strengths": "131K context|Gratis",
        "weaknesses": "Desconocido", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 131072
    },
    {
        "name": "Laguna M", "provider": "openrouter", "model_id": "poolside/laguna-m.1:free",
        "score": 66, "strengths": "262K context|Gratis",
        "weaknesses": "Desconocido", "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 262144
    },
    {
        "name": "Llama 3.2 3B (OR)", "provider": "openrouter", "model_id": "meta-llama/llama-3.2-3b-instruct:free",
        "score": 60, "strengths": "Rápido|131K context|Gratis",
        "weaknesses": "Solo 3B params", "capabilities": "math_problem|iq_puzzle|memory_game|quick_log|general",
        "context_window": 131072
    },
]

LM_STUDIO_MODEL = [
    {
        "name": "Local (LM Studio)", "provider": "lm_studio", "model_id": "local-model",
        "score": 50, "strengths": "Privado|Sin límites|Sin API key",
        "weaknesses": "Depende del modelo descargado|Más lento sin GPU",
        "capabilities": "math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|memory_coaching|general",
        "context_window": 4096
    }
]

def seed():
    from core.database import create_db_and_tables
    create_db_and_tables()
    with Session(engine) as session:
        existing = session.exec(select(AiModel)).all()
        if existing:
            print(f"La base ya tiene {len(existing)} modelos. Saltando poblado.")
            return

        print("Poblando tabla AiModel...")
        all_models = GROQ_MODELS + OPENROUTER_MODELS + LM_STUDIO_MODEL
        for m in all_models:
            model = AiModel(**m)
            session.add(model)

        session.commit()
        print("Modelos guardados exitosamente.")

if __name__ == "__main__":
    seed()
