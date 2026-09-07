import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlmodel import Field, SQLModel


class PaesCurriculumVersion(SQLModel, table=True):
    __tablename__ = "paes_curriculum_versions"

    id: str = Field(primary_key=True)
    code: str = Field(index=True, unique=True)
    name: str
    year: int
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PaesSubject(SQLModel, table=True):
    __tablename__ = "paes_subjects"

    id: str = Field(primary_key=True)
    curriculum_version_id: str = Field(foreign_key="paes_curriculum_versions.id", index=True)
    code: str = Field(index=True)
    name: str
    is_mandatory: bool = Field(default=True)
    total_questions: int = Field(default=65)
    scored_questions: int = Field(default=60)
    pilot_questions: int = Field(default=5)
    duration_minutes: int = Field(default=140)

class PaesCompetency(SQLModel, table=True):
    __tablename__ = "paes_competencies"

    id: str = Field(primary_key=True)
    code: str = Field(index=True, unique=True) # RESOLVER_PROBLEMAS, MODELAR, REPRESENTAR, ARGUMENTAR
    name: str
    description: Optional[str] = Field(default=None)

class PaesEjeTematico(SQLModel, table=True):
    __tablename__ = "paes_ejes_tematicos"

    id: str = Field(primary_key=True)
    subject_id: str = Field(foreign_key="paes_subjects.id", index=True)
    name: str
    order_index: int = Field(default=0)

class PaesTopic(SQLModel, table=True):
    __tablename__ = "paes_topics"

    id: str = Field(primary_key=True)
    eje_id: str = Field(foreign_key="paes_ejes_tematicos.id", index=True)
    name: str
    order_index: int = Field(default=0)

class PaesSubtopic(SQLModel, table=True):
    __tablename__ = "paes_subtopics"

    id: str = Field(primary_key=True)
    topic_id: str = Field(foreign_key="paes_topics.id", index=True)
    name: str
    slug: str = Field(index=True, unique=True)
    description: Optional[str] = Field(default=None)
    order_index: int = Field(default=0)

class PaesSubtopicPrerequisite(SQLModel, table=True):
    __tablename__ = "paes_subtopic_prerequisites"

    id: str = Field(primary_key=True)
    subtopic_id: str = Field(foreign_key="paes_subtopics.id", index=True)
    prerequisite_id: str = Field(foreign_key="paes_subtopics.id", index=True)
    relationship_type: str = Field(default="STRICT_PREREQUISITE")
    minimum_mastery_required: float = Field(default=0.60)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PaesQuestion(SQLModel, table=True):
    __tablename__ = "paes_questions"

    id: str = Field(primary_key=True)
    subtopic_id: str = Field(foreign_key="paes_subtopics.id", index=True)
    skill_id: str = Field(foreign_key="paes_competencies.id", index=True)
    provenance_type: str = Field(default="ORIGINAL") # OFFICIAL, ORIGINAL, PARAMETRIC
    stem: str
    stimulus_title: Optional[str] = Field(default=None)
    stimulus_text: Optional[str] = Field(default=None)
    options_json: str # JSON list of {key, text, is_correct, distractor_type}
    explanation_json: str # JSON dict {correct_solution, distractor_analysis}
    difficulty_estimate: float = Field(default=0.5)
    difficulty_source: str = Field(default="INITIAL_HEURISTIC")
    irt_a: Optional[float] = Field(default=None)
    irt_b: Optional[float] = Field(default=None)
    irt_c: Optional[float] = Field(default=None)
    irt_status: str = Field(default="UNINITIALIZED")
    is_pilot: bool = Field(default=False)
    source_attribution_json: str = Field(default="{}")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def options(self) -> List[Dict[str, Any]]:
        return json.loads(self.options_json) if self.options_json else []

    @property
    def explanation(self) -> Dict[str, Any]:
        return json.loads(self.explanation_json) if self.explanation_json else {}

class PaesLearningState(SQLModel, table=True):
    __tablename__ = "paes_learning_states"

    id: str = Field(primary_key=True)
    user_id: int = Field(index=True)
    subtopic_id: str = Field(foreign_key="paes_subtopics.id", index=True)
    mastery_score: float = Field(default=0.10)
    confidence_score: float = Field(default=0.10)
    leitner_box: int = Field(default=1)
    next_review_at: datetime = Field(default_factory=datetime.utcnow)
    fsrs_stability: Optional[float] = Field(default=None)
    fsrs_difficulty: Optional[float] = Field(default=None)
    recent_accuracy: float = Field(default=0.0)
    total_attempts: int = Field(default=0)
    total_successes: int = Field(default=0)
    last_practiced_at: datetime = Field(default_factory=datetime.utcnow)

class PaesAssessmentState(SQLModel, table=True):
    __tablename__ = "paes_assessment_states"

    id: str = Field(primary_key=True)
    user_id: int = Field(index=True)
    subject_id: str = Field(foreign_key="paes_subjects.id", index=True)
    theta: float = Field(default=0.0)
    theta_se: float = Field(default=1.0)
    theta_method: str = Field(default="HEURISTIC_SCORE")
    theta_status: str = Field(default="PROVISIONAL")
    estimated_paes_min: int = Field(default=450)
    estimated_paes_max: int = Field(default=550)
    total_scored_items_answered: int = Field(default=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PaesStudySession(SQLModel, table=True):
    __tablename__ = "paes_study_sessions"

    id: str = Field(primary_key=True)
    user_id: int = Field(index=True)
    session_mode: str = Field(default="PRACTICE") # PRACTICE, LEARN, EXAM, DIAGNOSTIC
    subject_id: Optional[str] = Field(default=None)
    subtopic_id: Optional[str] = Field(default=None)
    is_completed: bool = Field(default=False)
    total_items: int = Field(default=0)
    correct_items: int = Field(default=0)
    fatigue_index: float = Field(default=0.0)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

class PaesQuestionAttempt(SQLModel, table=True):
    __tablename__ = "paes_question_attempts"

    id: str = Field(primary_key=True)
    session_id: str = Field(foreign_key="paes_study_sessions.id", index=True)
    question_id: str = Field(foreign_key="paes_questions.id", index=True)
    user_id: int = Field(index=True)
    selected_option: str # A, B, C, D
    is_correct: bool
    time_spent_seconds: int = Field(default=30)
    perceived_confidence: int = Field(default=3) # 1-5
    mistake_cause: Optional[str] = Field(default=None) # CONCEPTUAL, PROCEDIMENTAL, CALCULO, etc.
    diagnostic_source: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PaesSocraticStep(SQLModel, table=True):
    __tablename__ = "paes_socratic_steps"

    id: str = Field(primary_key=True)
    session_id: str = Field(index=True)
    question_id: str = Field(index=True)
    tutor_level: int = Field(default=1) # 1 to 6
    hint_text: str
    student_response: Optional[str] = Field(default=None)
    student_understanding: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
