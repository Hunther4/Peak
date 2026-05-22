import sys
from pathlib import Path

# Asegurar path correcto
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from core.database import engine
from models.models import AiModel

GROQ_MODELS = [
    {
        "name": "Llama 3.1 70B", "provider": "groq", "model_id": "llama-3.1-70b-versatile",
        "score": 92, "strengths": "Razonamiento profundo|Código|Contexto 128K",
        "weaknesses": "Lento|Rate limit 30 req/min", "capabilities": "audit|code|reasoning",
        "context_window": 131072
    },
    {
        "name": "Llama 3.1 8B", "provider": "groq", "model_id": "llama-3.1-8b-instant",
        "score": 78, "strengths": "Rápido|Bueno para quick_log",
        "weaknesses": "Menos preciso en auditoría", "capabilities": "quick_log|general",
        "context_window": 131072
    },
    {
        "name": "Mixtral 8x7B", "provider": "groq", "model_id": "mixtral-8x7b-32768",
        "score": 85, "strengths": "Razonamiento|Multilingüe|Contexto 32K",
        "weaknesses": "Ocasionales alucinaciones", "capabilities": "audit|assessment|reasoning",
        "context_window": 32768
    },
    {
        "name": "Gemma 2 9B", "provider": "groq", "model_id": "gemma2-9b-it",
        "score": 75, "strengths": "Rápido|Instrucciones precisas",
        "weaknesses": "Contexto 8K limitado", "capabilities": "quick_log|general",
        "context_window": 8192
    }
]

OPENROUTER_MODELS = [
    {
        "name": "Llama 3.1 70B (OR)", "provider": "openrouter", "model_id": "meta-llama/llama-3.1-70b-instruct:free",
        "score": 91, "strengths": "Razonamiento profundo|Gratis",
        "weaknesses": "Rate limit|Lento en高峰期", "capabilities": "audit|code|reasoning",
        "context_window": 131072
    },
    {
        "name": "Mistral Nemo 12B", "provider": "openrouter", "model_id": "mistralai/mistral-nemo:free",
        "score": 82, "strengths": "Balance velocidad/calidad|Gratis",
        "weaknesses": "Contexto 12K medio", "capabilities": "audit|quick_log|assessment",
        "context_window": 12288
    },
    {
        "name": "DeepSeek V2.5", "provider": "openrouter", "model_id": "deepseek/deepseek-chat:free",
        "score": 88, "strengths": "Razonamiento técnico|Código|Gratis",
        "weaknesses": "A veces verboso", "capabilities": "audit|code|reasoning|assessment",
        "context_window": 65536
    },
    {
        "name": "Phi 3.5 Mini", "provider": "openrouter", "model_id": "microsoft/phi-3.5-mini-4k-instruct:free",
        "score": 70, "strengths": "Ligero|Rápido|Gratis",
        "weaknesses": "Contexto 4K|Limitado", "capabilities": "quick_log|general",
        "context_window": 4096
    }
]

LM_STUDIO_MODEL = [
    {
        "name": "Local (LM Studio)", "provider": "lm_studio", "model_id": "local-model",
        "score": 65, "strengths": "Privado|Sin límites|Sin API key",
        "weaknesses": "Depende del modelo descargado|Más lento sin GPU",
        "capabilities": "audit|quick_log|assessment|general",
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
