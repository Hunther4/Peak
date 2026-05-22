from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class CognitiveSkill(SQLModel, table=True):
    """Tipo de tarea cognitiva basada en fases psicométricas."""
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str
    fase_iq_base: int  # 100, 115, 130, 145, etc.

class CognitiveSession(SQLModel, table=True):
    """Telemetría global de una sesión de entrenamiento cerebral."""
    id: Optional[int] = Field(default=None, primary_key=True)
    cognitive_skill_id: int = Field(foreign_key="cognitiveskill.id")
    fecha_inicio: datetime = Field(default_factory=datetime.utcnow)
    fecha_fin: Optional[datetime] = None
    nivel_n_alcanzado: int = Field(default=1)
    tiempo_reaccion_promedio_ms: float = Field(default=0.0)
    tasa_precision: float = Field(default=0.0)

class CognitiveTrial(SQLModel, table=True):
    """Micro‑dato de cada estímulo/pregunta de la sesión."""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="cognitivesession.id")
    estimulo: str
    respuesta_esperada: str
    respuesta_usuario: str
    es_correcto: bool
    tiempo_reaccion_ms: int
