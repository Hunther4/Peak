import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True, max_length=200)
    name: str = Field(max_length=200)
    domain: str
    skill_type: str
    config_path: str
    current_level: float = Field(default=1.0)
    parent_id: Optional[int] = Field(default=None, foreign_key="skill.id", index=True)
    practice_level: Optional[str] = Field(default=None)  # "naive" | "purposeful" | "deliberate"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    sessions: list["Session"] = Relationship(back_populates="skill")
    assessments: list["Assessment"] = Relationship(back_populates="skill")
    mental_reps: list["MentalRep"] = Relationship(back_populates="skill")
    challenges: list["Challenge"] = Relationship(back_populates="skill")


class Session(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", ondelete="CASCADE", index=True)
    duration_minutes: int
    timer_elapsed_sec: Optional[int] = None
    what_i_practiced: str = Field(max_length=2000)
    difficulty: int = Field(ge=1, le=5)
    micro_error_found: Optional[str] = Field(default=None, max_length=1000)
    correction_applied: Optional[str] = None
    hypothesis_tomorrow: Optional[str] = None
    entry_mode: str = Field(default="quick")  # "quick" | "full"
    ai_fields_status: str = Field(default="pending")  # "pending" | "completed"
    was_deliberate: Optional[bool] = None
    ai_audit_log: Optional[str] = None  # JSON string
    onboarding_mode: bool = Field(default=True)
    session_data: Optional[str] = None  # JSON string
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    skill: Optional[Skill] = Relationship(back_populates="sessions")

    def get_ai_audit_log(self):
        if self.ai_audit_log:
            return json.loads(self.ai_audit_log)
        return None

    def get_session_data(self):
        if self.session_data:
            return json.loads(self.session_data)
        return None


class Assessment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", ondelete="CASCADE", index=True)
    type: str  # "probe" | "formal"
    score: float
    metrics_json: Optional[str] = None  # JSON string
    notes: Optional[str] = Field(default=None, max_length=2000)
    linked_session_id: Optional[int] = Field(default=None, foreign_key="session.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    skill: Optional[Skill] = Relationship(back_populates="assessments")

    def get_metrics(self):
        if self.metrics_json:
            return json.loads(self.metrics_json)
        return {}


class MentalRep(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", ondelete="CASCADE", index=True)
    description: str = Field(max_length=2000)
    version: int = Field(default=1)
    trigger: str  # "assessment" | "insight" | "session_batch"
    previous_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    skill: Optional[Skill] = Relationship(back_populates="mental_reps")


class Challenge(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", ondelete="CASCADE", index=True)
    description: str
    difficulty_target: int = Field(ge=1, le=5)
    source_book: Optional[str] = None
    source_chunk_id: Optional[str] = None
    linked_assessment_id: Optional[int] = Field(default=None, foreign_key="assessment.id", ondelete="CASCADE")
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    skill: Optional[Skill] = Relationship(back_populates="challenges")

class AiModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str                                   # "Llama 3.1 8B", "Mistral 7B", etc.
    provider: str                               # "groq" | "openrouter" | "lm_studio"
    model_id: str                               # ID real en el API ("llama3.1-8b-8192", etc.)
    is_free: bool = Field(default=True)
    score: int = Field(default=70, ge=0, le=100)  # Puntuación general 0-100
    strengths: Optional[str] = None             # Texto: fortalezas separadas por |
    weaknesses: Optional[str] = None            # Texto: debilidades separadas por |
    capabilities: Optional[str] = None          # Tags: "audit|quick_log|assessment|code|reasoning"
    context_window: int = Field(default=4096)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AppSetting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    value: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserProfile(SQLModel, table=True):
    """Simple user identity — no auth, just name + age for the welcome screen."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    age: int = Field(ge=1, le=150)
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryNumberSession(SQLModel, table=True):
    """Tracks a single game session for the Memory Number skill."""
    id: Optional[int] = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", ondelete="CASCADE", index=True)
    phase: int = Field(default=1, ge=1, le=7)
    current_span: int = Field(default=4, ge=4)
    consecutive_correct: int = Field(default=0, ge=0)
    consecutive_incorrect: int = Field(default=0, ge=0)
    best_span: int = Field(default=4, ge=4)
    best_phase: int = Field(default=1, ge=1, le=7)
    total_rounds: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    consolidated_session_id: Optional[int] = Field(default=None, foreign_key="session.id", ondelete="SET NULL")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    rounds: list["MemoryNumberRound"] = Relationship(back_populates="game_session")


class MemoryNumberRound(SQLModel, table=True):
    """A single round in a Memory Number game session — one sequence to recall."""
    id: Optional[int] = Field(default=None, primary_key=True)
    game_session_id: int = Field(foreign_key="memorynumbersession.id", ondelete="CASCADE", index=True)
    phase: int = Field(ge=1, le=7)
    span: int = Field(ge=4)
    digit_max: int = Field(default=1, ge=1)
    numbers_json: str  # JSON array of integers
    sequence_length: int
    ai_assisted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    game_session: Optional[MemoryNumberSession] = Relationship(back_populates="rounds")
    attempts: list["MemoryNumberAttempt"] = Relationship(back_populates="round")


class MemoryNumberAttempt(SQLModel, table=True):
    """A user's recall attempt for a given round."""
    id: Optional[int] = Field(default=None, primary_key=True)
    round_id: int = Field(foreign_key="memorynumberround.id", ondelete="CASCADE", index=True)
    submitted_numbers_json: str  # JSON array of integers
    correct: bool
    correct_positions: int = Field(default=0, ge=0)
    total_positions: int = Field(default=0, ge=0)
    errors_json: Optional[str] = None  # JSON array of error objects
    attempt_number: int = Field(default=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    round: Optional[MemoryNumberRound] = Relationship(back_populates="attempts")


class MathThinkingSession(SQLModel, table=True):
    """Tracks one game session for Math Thinking."""
    id: Optional[int] = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", ondelete="CASCADE", index=True)
    level: int = Field(default=1, ge=1, le=10)
    consecutive_correct: int = Field(default=0, ge=0)
    consecutive_incorrect: int = Field(default=0, ge=0)
    total_rounds: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    best_level: int = Field(default=1, ge=1, le=10)
    consolidated_session_id: Optional[int] = Field(default=None, foreign_key="session.id", ondelete="SET NULL")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    rounds: list["MathThinkingRound"] = Relationship(back_populates="session")


class MathThinkingRound(SQLModel, table=True):
    """A single problem in a Math Thinking session."""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="maththinkingsession.id", ondelete="CASCADE", index=True)
    level: int
    problem_text: str
    correct_answer: float
    solution_steps_json: Optional[str] = None  # JSON array of strings
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    session: Optional[MathThinkingSession] = Relationship(back_populates="rounds")
    attempts: list["MathThinkingAttempt"] = Relationship(back_populates="round")


class MathThinkingAttempt(SQLModel, table=True):
    """A user's answer submission for a Math Thinking round."""
    id: Optional[int] = Field(default=None, primary_key=True)
    round_id: int = Field(foreign_key="maththinkinground.id", ondelete="CASCADE", index=True)
    user_answer: float
    correct: bool
    solution_steps_json: Optional[str] = None  # JSON array of strings (returned on error)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    round: Optional[MathThinkingRound] = Relationship(back_populates="attempts")


class IQPracticeSession(SQLModel, table=True):
    """Tracks one game session for IQ Practice."""
    id: Optional[int] = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", ondelete="CASCADE", index=True)
    level: int = Field(default=1, ge=1, le=10)
    consecutive_correct: int = Field(default=0, ge=0)
    consecutive_incorrect: int = Field(default=0, ge=0)
    total_rounds: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    best_level: int = Field(default=1, ge=1, le=10)
    consolidated_session_id: Optional[int] = Field(default=None, foreign_key="session.id", ondelete="SET NULL")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    rounds: list["IQPracticeRound"] = Relationship(back_populates="session")


class IQPracticeRound(SQLModel, table=True):
    """A single puzzle in an IQ Practice session."""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="iqpracticesession.id", ondelete="CASCADE", index=True)
    level: int
    puzzle_type: str  # number_sequence | verbal_analogy | logical | pattern
    question: str
    options_json: str  # JSON array of 4 strings
    correct_answer: str  # The correct option text
    explanation: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    session: Optional[IQPracticeSession] = Relationship(back_populates="rounds")
    attempts: list["IQPracticeAttempt"] = Relationship(back_populates="round")


class IQPracticeAttempt(SQLModel, table=True):
    """A user's answer submission for an IQ Practice round."""
    id: Optional[int] = Field(default=None, primary_key=True)
    round_id: int = Field(foreign_key="iqpracticeround.id", ondelete="CASCADE", index=True)
    user_answer: str
    correct: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    round: Optional[IQPracticeRound] = Relationship(back_populates="attempts")


# =============================================================================
# Learning Patterns — Error tracking for adaptive AI prompts
# =============================================================================


class LearningPattern(SQLModel, table=True):
    """Raw per-attempt error metadata. One row per incorrect attempt."""
    id: Optional[int] = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", ondelete="CASCADE", index=True)
    skill_type: str  # "problem_set" | "iq_practice" | "memory_number"
    session_id: int = Field(index=True)  # game session ID (math/iq/memory)
    round_id: int = Field(index=True)  # round/puzzle ID
    attempt_id: int = Field(index=True)  # attempt ID
    error_type: str  # e.g. "arithmetic", "conceptual", "timeout", "careless"
    error_detail: Optional[str] = None  # free-text context
    level: int  # difficulty level at time of error
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


class ErrorPattern(SQLModel, table=True):
    """Aggregated error counts per skill + error type. Updated on each attempt."""
    id: Optional[int] = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", ondelete="CASCADE", index=True)
    skill_type: str  # "problem_set" | "iq_practice" | "memory_number"
    error_type: str  # "arithmetic" | "conceptual" | "timeout" | "careless"
    count: int = Field(default=0, ge=0)
    severity: float = Field(default=0.0, ge=0.0, le=1.0)  # 0.0 = none, 1.0 = critical
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("skill_id", "error_type", name="uq_errorpattern_skill_type"),
    )


class SessionError(SQLModel, table=True):
    """Links a game session to its error patterns with confidence scores."""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int  # game session ID — discriminator (maththinking/memory/iq), no FK
    session_type: str  # "math_thinking" | "iq_practice" | "memory_number"
    error_pattern_id: int = Field(foreign_key="errorpattern.id", ondelete="CASCADE")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    error_pattern: Optional[ErrorPattern] = Relationship()


# =============================================================================
# Skill Level History — Adaptive staircase tracking
# =============================================================================


class SkillLevelHistory(SQLModel, table=True):
    """Tracks every level change for a skill via the adaptive staircase.

    Each row records one staircase evaluation: the success/failure result,
    the level before and after, and what triggered the evaluation.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id", ondelete="CASCADE", index=True)
    success: bool  # True = session was successful, False = failure
    level_before: float
    level_after: float
    delta: float  # level_after - level_before (+1, -1, or 0)
    trigger: str  # "session_consolidation" | "assessment"
    session_id: Optional[int] = Field(default=None, foreign_key="session.id", ondelete="SET NULL")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
