"""
Corre esto UNA sola vez para crear las skills iniciales.
python seed.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from core.database import engine, create_db_and_tables
from models.models import Skill, AiModel

SKILLS = [
    {
        "slug": "iq-practice",
        "name": "Práctica de IQ",
        "domain": "cognitive",
        "skill_type": "placeholder",
        "config_path": "skills/iq-practice.yaml",
        "current_level": 1.0
    },
    {
        "slug": "math-thinking",
        "name": "Pensamiento Matemático",
        "domain": "math",
        "skill_type": "problem_set",
        "config_path": "skills/math-thinking.yaml",
        "current_level": 1.0
    },
    {
        "slug": "memory-number",
        "name": "Memorizar Números",
        "domain": "cognitive",
        "skill_type": "memory_number",
        "config_path": "skills/memory-number.yaml",
        "current_level": 1.0
    }
]

MODELS = [
    # ── Groq free-tier ──
    AiModel(name="Llama 3 8B", provider="groq", model_id="llama3-8b-8192", capabilities="audit|quick_log|assessment|general", score=85, is_active=True),
    AiModel(name="Llama 3 70B", provider="groq", model_id="llama3-70b-8192", capabilities="audit|quick_log|assessment|general", score=92, is_active=True),
    AiModel(name="Mixtral 8x7B", provider="groq", model_id="mixtral-8x7b-32768", capabilities="audit|quick_log|assessment|general", score=80, is_active=True),
    AiModel(name="Gemma 2 9B", provider="groq", model_id="gemma2-9b-it", capabilities="audit|quick_log|assessment|general", score=78, is_active=True),
    # ── OpenRouter free-tier ──
    AiModel(name="Mistral 7B", provider="openrouter", model_id="mistralai/mistral-7b-instruct", capabilities="audit|quick_log|assessment|general", score=75, is_active=True),
    # ── LM Studio local ──
    AiModel(name="Local Model", provider="lm_studio", model_id="local-model", capabilities="audit|quick_log|assessment|general", score=50, is_active=True),
]

def seed_models():
    """Seed default AI models if DB is empty."""
    with Session(engine) as db:
        existing = db.exec(select(AiModel).limit(1)).first()
        if existing:
            print("[i] Modelos ya existen, saltando seed.")
            return

        for m in MODELS:
            db.add(m)
            print(f"[+] Modelo añadido: {m.provider}/{m.name}")
        db.commit()
        print(f"[+] {len(MODELS)} modelos insertados.")

def seed():
    create_db_and_tables()
    with Session(engine) as db:
        for skill_data in SKILLS:
            existing = db.exec(
                select(Skill).where(Skill.slug == skill_data["slug"])
            ).first()
            if not existing:
                skill = Skill(**skill_data)
                db.add(skill)
                print(f"[+] Skill creada: {skill_data['name']}")
            else:
                print(f"[i] Skill ya existe: {skill_data['name']}")
        db.commit()
    seed_models()
    print("Seed completado.")

if __name__ == "__main__":
    seed()
