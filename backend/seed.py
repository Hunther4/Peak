"""
Corre esto UNA sola vez para crear las skills iniciales.
python seed.py
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select

from core.database import create_db_and_tables, engine
from models.cognitive_models import CognitiveSkill
from models.models import AiModel, Skill

logger = logging.getLogger(__name__)

SKILLS = [
    {
        "slug": "math-thinking",
        "name": "Pensamiento Matemático",
        "domain": "math",
        "skill_type": "problem_set",
        "config_path": "skills/math-thinking.yaml",
        "current_level": 1.0,
    },
    {
        "slug": "memory-number",
        "name": "Memoria de Trabajo",
        "domain": "cognitive",
        "skill_type": "memory_number",
        "config_path": "skills/memory-number.yaml",
        "current_level": 1.0,
    },
    {
        "slug": "iq-practice",
        "name": "Estimulación Cognitiva",
        "domain": "cognitive",
        "skill_type": "iq_practice",
        "config_path": "skills/iq-practice.yaml",
        "current_level": 1.0,
    },
    {
        "slug": "atencion-velocidad",
        "name": "Atención y Velocidad",
        "domain": "cognitive",
        "skill_type": "problem_set",
        "config_path": "skills/atencion-velocidad.yaml",
        "current_level": 1.0,
    },
]

SUB_SKILLS = [
    # === Pensamiento Matemático ===
    {"slug": "math-aritmetica", "name": "Aritmética", "parent_slug": "math-thinking",
     "skill_type": "problem_set", "domain": "math", "config_path": "skills/math-thinking.yaml"},
    {"slug": "math-algebra", "name": "Álgebra", "parent_slug": "math-thinking",
     "skill_type": "problem_set", "domain": "math", "config_path": "skills/math-thinking.yaml"},
    {"slug": "math-geometria", "name": "Geometría", "parent_slug": "math-thinking",
     "skill_type": "problem_set", "domain": "math", "config_path": "skills/math-thinking.yaml"},
    {"slug": "math-secuencias", "name": "Secuencias Lógicas", "parent_slug": "math-thinking",
     "skill_type": "problem_set", "domain": "math", "config_path": "skills/math-thinking.yaml"},

    # === Memoria de Trabajo ===
    {"slug": "mem-span", "name": "Span de dígitos", "parent_slug": "memory-number",
     "skill_type": "memory_number", "domain": "cognitive", "config_path": "skills/memory-number.yaml"},
    {"slug": "mem-dual-nback", "name": "Dual N-Back", "parent_slug": "memory-number",
     "skill_type": "dual_n_back", "domain": "cognitive", "config_path": "skills/dual-n-back.yaml"},
    {"slug": "mem-visual", "name": "Memoria visual", "parent_slug": "memory-number",
     "skill_type": "memory_number", "domain": "cognitive", "config_path": "skills/memory-number.yaml"},

    # === Estimulación Cognitiva ===
    {"slug": "iq-secuencias", "name": "Secuencias numéricas", "parent_slug": "iq-practice",
     "skill_type": "iq_practice", "domain": "cognitive", "config_path": "skills/iq-practice.yaml"},
    {"slug": "iq-analogias", "name": "Analogías verbales", "parent_slug": "iq-practice",
     "skill_type": "iq_practice", "domain": "cognitive", "config_path": "skills/iq-practice.yaml"},
    {"slug": "iq-matrices", "name": "Matrices", "parent_slug": "iq-practice",
     "skill_type": "iq_practice", "domain": "cognitive", "config_path": "skills/iq-practice.yaml"},

    # === Atención y Velocidad ===
    {"slug": "atencion-lectura", "name": "Lectura veloz", "parent_slug": "atencion-velocidad",
     "skill_type": "problem_set", "domain": "cognitive", "config_path": "skills/atencion-velocidad.yaml"},
    {"slug": "atencion-busqueda", "name": "Búsqueda visual", "parent_slug": "atencion-velocidad",
     "skill_type": "iq_practice", "domain": "cognitive", "config_path": "skills/atencion-velocidad.yaml"},
    {"slug": "atencion-timer", "name": "Timer challenges", "parent_slug": "atencion-velocidad",
     "skill_type": "problem_set", "domain": "cognitive", "config_path": "skills/atencion-velocidad.yaml"},
]

MODELS = [
    # ── Groq (6 models, fast, priority) ──
    AiModel(name="Llama 3.1 8B", provider="groq", model_id="llama-3.1-8b-instant", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=95, is_active=True, context_window=131072),
    AiModel(name="Llama 3.3 70B", provider="groq", model_id="llama-3.3-70b-versatile", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=93, is_active=True, context_window=131072),
    AiModel(name="Llama 4 Scout 17B", provider="groq", model_id="meta-llama/llama-4-scout-17b-16e-instruct", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=91, is_active=True, context_window=131072),
    AiModel(name="Qwen3 32B", provider="groq", model_id="qwen/qwen3-32b", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=90, is_active=True, context_window=131072),
    AiModel(name="GPT-OSS 120B (Groq)", provider="groq", model_id="openai/gpt-oss-120b", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=88, is_active=True, context_window=131072),
    AiModel(name="GPT-OSS 20B (Groq)", provider="groq", model_id="openai/gpt-oss-20b", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=82, is_active=True, context_window=131072),
    # ── OpenRouter free-tier (16 models) ──
    AiModel(name="Qwen3 Coder", provider="openrouter", model_id="qwen/qwen3-coder:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=87, is_active=True, context_window=1048576),
    AiModel(name="Nemotron 3 Super 120B", provider="openrouter", model_id="nvidia/nemotron-3-super-120b-a12b:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=86, is_active=True, context_window=1000000),
    AiModel(name="Hermes 3 405B", provider="openrouter", model_id="nousresearch/hermes-3-llama-3.1-405b:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=85, is_active=True, context_window=131072),
    AiModel(name="GPT-OSS 120B (OR)", provider="openrouter", model_id="openai/gpt-oss-120b:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=84, is_active=True, context_window=131072),
    AiModel(name="Kimi K2.6", provider="openrouter", model_id="moonshotai/kimi-k2.6:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=83, is_active=True, context_window=262144),
    AiModel(name="Gemma 4 31B", provider="openrouter", model_id="google/gemma-4-31b-it:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=81, is_active=True, context_window=262144),
    AiModel(name="Qwen3 Next 80B", provider="openrouter", model_id="qwen/qwen3-next-80b-a3b-instruct:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=80, is_active=True, context_window=262144),
    AiModel(name="Llama 3.3 70B (OR)", provider="openrouter", model_id="meta-llama/llama-3.3-70b-instruct:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=79, is_active=True, context_window=131072),
    AiModel(name="Gemma 4 26B", provider="openrouter", model_id="google/gemma-4-26b-a4b-it:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=78, is_active=True, context_window=262144),
    AiModel(name="Nemotron 3 Nano 30B", provider="openrouter", model_id="nvidia/nemotron-3-nano-30b-a3b:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=77, is_active=True, context_window=256000),
    AiModel(name="Nemotron Nano 12B VL", provider="openrouter", model_id="nvidia/nemotron-nano-12b-v2-vl:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=76, is_active=True, context_window=128000),
    AiModel(name="Nemotron Nano 9B", provider="openrouter", model_id="nvidia/nemotron-nano-9b-v2:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=75, is_active=True, context_window=128000),
    AiModel(name="GPT-OSS 20B (OR)", provider="openrouter", model_id="openai/gpt-oss-20b:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=74, is_active=True, context_window=131072),
    AiModel(name="GLM 4.5 Air", provider="openrouter", model_id="z-ai/glm-4.5-air:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=73, is_active=True, context_window=131072),
    AiModel(name="Laguna M", provider="openrouter", model_id="poolside/laguna-m.1:free", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=72, is_active=True, context_window=262144),
    AiModel(name="Llama 3.2 3B (OR)", provider="openrouter", model_id="meta-llama/llama-3.2-3b-instruct:free", capabilities="math_problem|iq_puzzle|memory_game|quick_log|general", score=65, is_active=True, context_window=131072),
    # ── LM Studio local (fallback) ──
    AiModel(name="Local Model", provider="lm_studio", model_id="local-model", capabilities="math_problem|iq_puzzle|memory_game|audit|quick_log|assessment|general", score=70, is_active=True, context_window=50000),
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


COGNITIVE_SKILLS = [
    {
        "nombre": "Dual N-Back",
        "descripcion": "Entrenamiento de memoria de trabajo con estímulos visuales y auditivos simultáneos. Basado en Jaeggi et al. (2008).",
        "fase_iq_base": 100
    }
]


def seed_cognitive_skills():
    """Seed cognitive skills if DB is empty."""
    with Session(engine) as db:
        existing = db.exec(select(CognitiveSkill).limit(1)).first()
        if existing:
            return
        for cs in COGNITIVE_SKILLS:
            skill = CognitiveSkill(**cs)
            db.add(skill)
            print(f"[+] CognitiveSkill creada: {cs['nombre']}")
        db.commit()


def seed():
    create_db_and_tables()
    seed_cognitive_skills()
    with Session(engine) as db:
        # 1. Create/update root skills
        for skill_data in SKILLS:
            existing = db.exec(
                select(Skill).where(Skill.slug == skill_data["slug"])
            ).first()
            if existing:
                for key, value in skill_data.items():
                    setattr(existing, key, value)
                db.add(existing)
                print(f"[~] Skill actualizada: {skill_data['name']}")
            else:
                skill = Skill(**skill_data)
                db.add(skill)
                print(f"[+] Skill creada: {skill_data['name']}")

        # 2. Migrate dual-n-back from root to sub-skill of memory-number
        dual_root = db.exec(
            select(Skill).where(Skill.slug == "dual-n-back")
        ).first()
        memory_root = db.exec(
            select(Skill).where(Skill.slug == "memory-number")
        ).first()
        if dual_root and memory_root and dual_root.parent_id is None:
            dual_root.parent_id = memory_root.id
            dual_root.name = "Dual N-Back"
            db.add(dual_root)
            print("[~] Dual N-Back migrado a sub-skill de Memoria de Trabajo")

        # 3. Create sub-skills
        roots = {}
        for s in db.exec(select(Skill).where(Skill.parent_id is None)).all():
            roots[s.slug] = s.id

        for sub in SUB_SKILLS:
            existing = db.exec(
                select(Skill).where(Skill.slug == sub["slug"])
            ).first()
            if existing:
                continue

            parent_id = roots.get(sub["parent_slug"])
            if not parent_id:
                logger.warning("Parent not found for %s", sub["slug"])
                continue

            skill = Skill(
                slug=sub["slug"],
                name=sub["name"],
                domain=sub["domain"],
                skill_type=sub["skill_type"],
                config_path=sub["config_path"],
                current_level=1.0,
                parent_id=parent_id,
            )
            db.add(skill)
            print(f"[+] Sub-skill creada: {sub['name']} → {sub['parent_slug']}")

        db.commit()

    seed_models()
    print("Seed completado.")


if __name__ == "__main__":
    seed()
