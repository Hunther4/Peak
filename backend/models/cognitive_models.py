from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class CognitiveSkill(SQLModel, table=True):
    """Tipo de tarea cognitiva basada en fases psicométricas."""
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str
    fase_iq_base: int  # 100, 115, 130, 145, etc.
    nivel_n_actual: int = Field(default=1, ge=1)

class CognitiveSession(SQLModel, table=True):
    """Telemetría global de una sesión de entrenamiento cerebral."""
    id: Optional[int] = Field(default=None, primary_key=True)
    cognitive_skill_id: int = Field(foreign_key="cognitiveskill.id", ondelete="CASCADE")
    fecha_inicio: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fecha_fin: Optional[datetime] = None
    nivel_n_alcanzado: int = Field(default=1)
    tiempo_reaccion_promedio_ms: float = Field(default=0.0)
    tasa_precision: float = Field(default=0.0)
    consolidated_session_id: Optional[int] = Field(default=None, foreign_key="session.id", ondelete="SET NULL")

class CognitiveTrial(SQLModel, table=True):
    """Micro‑dato de cada estímulo/pregunta de la sesión."""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="cognitivesession.id", ondelete="CASCADE")
    estimulo: str
    respuesta_esperada: str
    respuesta_usuario: str
    es_correcto: bool
    tiempo_reaccion_ms: int


# --- WU 4: Memory Session & Strategy Tracking ---

class MemorySessionMeta(SQLModel, table=True):
    """Strategy metadata for a Memory Number game session.

    Tracks which memory strategy the user reports using (chunking,
    rehearsal, method of loci, etc.) and self-reported difficulty.
    Links to MemoryNumberSession for round-level detail.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    game_session_id: int = Field(
        foreign_key="memorynumbersession.id", ondelete="CASCADE", index=True
    )
    strategy_type: str = Field(
        default="none",
        description="Primary strategy: chunking, rehearsal, method_of_loci, none, other",
    )
    self_reported_difficulty: Optional[int] = Field(
        default=None, ge=1, le=5,
        description="1=easy, 5=hard — user self-report after session",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Free-text notes about strategy or experience",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryStrategyLog(SQLModel, table=True):
    """Per-round strategy observation for Memory Number.

    Records which strategy was attempted for a specific round and
    whether it was effective (all correct = effective). Used to
    correlate strategy types with accuracy at different spans.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    game_session_id: int = Field(
        foreign_key="memorynumbersession.id", ondelete="CASCADE", index=True
    )
    round_id: int = Field(
        foreign_key="memorynumberround.id", ondelete="CASCADE", index=True
    )
    strategy_used: str = Field(
        default="none",
        description="Strategy used for this round: chunking, rehearsal, grouping, none",
    )
    effective: bool = Field(
        default=False,
        description="True if all positions were correct",
    )
    span_at_attempt: int = Field(ge=4, description="Span when this attempt was made")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
