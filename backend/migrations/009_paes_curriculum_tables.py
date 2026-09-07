"""009 — PAES Adaptive Curriculum, Questions, FSRS State, and Study Sessions.

Creates tables for the PAES M1 unified integration:
- paes_curriculum_versions
- paes_subjects
- paes_competencies
- paes_ejes_tematicos
- paes_topics
- paes_subtopics
- paes_subtopic_prerequisites
- paes_questions
- paes_learning_states
- paes_assessment_states
- paes_study_sessions
- paes_question_attempts
- paes_socratic_steps
"""

import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)

def up(conn):
    """Create paes_* tables and associated performance indexes."""
    logger.info("Applying migration 009: Creating paes_* curriculum and telemetry tables")

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_curriculum_versions (
            id TEXT PRIMARY KEY,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            year INTEGER NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_subjects (
            id TEXT PRIMARY KEY,
            curriculum_version_id TEXT NOT NULL REFERENCES paes_curriculum_versions(id) ON DELETE CASCADE,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            is_mandatory BOOLEAN NOT NULL DEFAULT 1,
            total_questions INTEGER NOT NULL DEFAULT 65,
            scored_questions INTEGER NOT NULL DEFAULT 60,
            pilot_questions INTEGER NOT NULL DEFAULT 5,
            duration_minutes INTEGER NOT NULL DEFAULT 140
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_competencies (
            id TEXT PRIMARY KEY,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_ejes_tematicos (
            id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL REFERENCES paes_subjects(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            order_index INTEGER NOT NULL DEFAULT 0
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_topics (
            id TEXT PRIMARY KEY,
            eje_id TEXT NOT NULL REFERENCES paes_ejes_tematicos(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            order_index INTEGER NOT NULL DEFAULT 0
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_subtopics (
            id TEXT PRIMARY KEY,
            topic_id TEXT NOT NULL REFERENCES paes_topics(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            description TEXT,
            order_index INTEGER NOT NULL DEFAULT 0
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_subtopic_prerequisites (
            id TEXT PRIMARY KEY,
            subtopic_id TEXT NOT NULL REFERENCES paes_subtopics(id) ON DELETE CASCADE,
            prerequisite_id TEXT NOT NULL REFERENCES paes_subtopics(id) ON DELETE CASCADE,
            relationship_type TEXT NOT NULL DEFAULT 'STRICT_PREREQUISITE',
            minimum_mastery_required REAL NOT NULL DEFAULT 0.60,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_questions (
            id TEXT PRIMARY KEY,
            subtopic_id TEXT NOT NULL REFERENCES paes_subtopics(id) ON DELETE RESTRICT,
            skill_id TEXT NOT NULL REFERENCES paes_competencies(id) ON DELETE RESTRICT,
            provenance_type TEXT NOT NULL DEFAULT 'ORIGINAL',
            stem TEXT NOT NULL,
            options_json TEXT NOT NULL,
            explanation_json TEXT NOT NULL,
            difficulty_estimate REAL NOT NULL DEFAULT 0.5,
            difficulty_source TEXT NOT NULL DEFAULT 'INITIAL_HEURISTIC',
            irt_a REAL,
            irt_b REAL,
            irt_c REAL,
            irt_status TEXT NOT NULL DEFAULT 'UNINITIALIZED',
            is_pilot BOOLEAN NOT NULL DEFAULT 0,
            source_attribution_json TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_learning_states (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            subtopic_id TEXT NOT NULL REFERENCES paes_subtopics(id) ON DELETE CASCADE,
            mastery_score REAL NOT NULL DEFAULT 0.10,
            confidence_score REAL NOT NULL DEFAULT 0.10,
            leitner_box INTEGER NOT NULL DEFAULT 1,
            next_review_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            fsrs_stability REAL,
            fsrs_difficulty REAL,
            recent_accuracy REAL NOT NULL DEFAULT 0.0,
            total_attempts INTEGER NOT NULL DEFAULT 0,
            total_successes INTEGER NOT NULL DEFAULT 0,
            last_practiced_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_assessment_states (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            subject_id TEXT NOT NULL REFERENCES paes_subjects(id) ON DELETE CASCADE,
            theta REAL NOT NULL DEFAULT 0.0,
            theta_se REAL NOT NULL DEFAULT 1.0,
            theta_method TEXT NOT NULL DEFAULT 'HEURISTIC_SCORE',
            theta_status TEXT NOT NULL DEFAULT 'PROVISIONAL',
            estimated_paes_min INTEGER NOT NULL DEFAULT 450,
            estimated_paes_max INTEGER NOT NULL DEFAULT 550,
            total_scored_items_answered INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_study_sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            session_mode TEXT NOT NULL DEFAULT 'PRACTICE',
            subject_id TEXT,
            subtopic_id TEXT,
            is_completed BOOLEAN NOT NULL DEFAULT 0,
            total_items INTEGER NOT NULL DEFAULT 0,
            correct_items INTEGER NOT NULL DEFAULT 0,
            fatigue_index REAL NOT NULL DEFAULT 0.0,
            started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_question_attempts (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES paes_study_sessions(id) ON DELETE CASCADE,
            question_id TEXT NOT NULL REFERENCES paes_questions(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL,
            selected_option TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            time_spent_seconds INTEGER NOT NULL DEFAULT 30,
            perceived_confidence INTEGER NOT NULL DEFAULT 3,
            mistake_cause TEXT,
            diagnostic_source TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS paes_socratic_steps (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            tutor_level INTEGER NOT NULL DEFAULT 1,
            hint_text TEXT NOT NULL,
            student_response TEXT,
            student_understanding TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # Indexes
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_paes_subtopics_slug ON paes_subtopics(slug)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_paes_questions_subtopic ON paes_questions(subtopic_id)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_paes_learning_user ON paes_learning_states(user_id)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_paes_attempts_session ON paes_question_attempts(session_id)"))

    logger.info("Migration 009 complete.")

MIGRATION = {
    "version": 9,
    "name": "paes_curriculum_tables",
    "up": up,
}
