"""
Corre esto UNA sola vez para crear las skills iniciales.
python seed.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session
from core.database import engine, create_db_and_tables
from models.models import Skill

SKILLS = [
    {
        "slug": "memory",
        "name": "Memoria",
        "domain": "memory",
        "skill_type": "staircase",
        "config_path": "skills/memory.yaml",
        "current_level": 1.0
    },
    {
        "slug": "math",
        "name": "Matemáticas",
        "domain": "math",
        "skill_type": "problem_set",
        "config_path": "skills/math.yaml",
        "current_level": 1.0
    }
]

def seed():
    create_db_and_tables()
    with Session(engine) as db:
        for skill_data in SKILLS:
            from sqlmodel import select
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
    print("Seed completado.")

if __name__ == "__main__":
    seed()
