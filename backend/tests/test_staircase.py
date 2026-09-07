"""Tests for the adaptive staircase service.

Covers: apply_staircase, detect_plateau, compute_practice_level, determine_session_success.
"""
from sqlmodel import select

from models.models import SkillLevelHistory
from services.staircase import (
    apply_staircase,
    compute_practice_level,
    detect_plateau,
    determine_session_success,
    get_recent_results,
)

# ─── apply_staircase ──────────────────────────────────────────────


def test_staircase_first_session_no_move(session, skill_factory):
    """First session should record but not move level."""
    skill = skill_factory(level=5.0)
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()

    assert skill.current_level == 5.0  # No change
    history = session.exec(
        select(SkillLevelHistory).where(SkillLevelHistory.skill_id == skill.id)
    ).all()
    assert len(history) == 1
    assert history[0].success is True
    assert history[0].delta == 0.0


def test_staircase_second_session_no_move(session, skill_factory):
    """Second session should record but not move level (need 2+ in window)."""
    skill = skill_factory(level=5.0)
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()

    assert skill.current_level == 5.0  # Still no change
    history = session.exec(
        select(SkillLevelHistory).where(SkillLevelHistory.skill_id == skill.id)
    ).all()
    assert len(history) == 2


def test_staircase_up(session, skill_factory):
    """3 successes → level up by 1."""
    skill = skill_factory(level=5.0)
    for _ in range(2):  # First 2 = no move
        apply_staircase(session, skill, True, trigger="session_consolidation")
        session.commit()
    apply_staircase(session, skill, True, trigger="session_consolidation")  # 3rd → up
    session.commit()

    assert skill.current_level == 6.0


def test_staircase_down(session, skill_factory):
    """3 failures → level down by 1."""
    skill = skill_factory(level=5.0)
    for _ in range(2):
        apply_staircase(session, skill, False, trigger="session_consolidation")
        session.commit()
    apply_staircase(session, skill, False, trigger="session_consolidation")
    session.commit()

    assert skill.current_level == 4.0


def test_staircase_mixed(session, skill_factory):
    """Mixed results → maintain level."""
    skill = skill_factory(level=5.0)
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()
    apply_staircase(session, skill, False, trigger="session_consolidation")  # 2/3 = 67% → up
    session.commit()

    # 2 successes + 1 failure = 66.7% → exactly at boundary, should maintain
    # Actually 2/3 = 0.666... which is < 0.67, so should maintain
    assert skill.current_level == 5.0


def test_staircase_bounds_low(session, skill_factory):
    """Level 1 + failure → stays at 1."""
    skill = skill_factory(level=1.0)
    for _ in range(2):
        apply_staircase(session, skill, False, trigger="session_consolidation")
        session.commit()
    apply_staircase(session, skill, False, trigger="session_consolidation")
    session.commit()

    assert skill.current_level == 1.0


def test_staircase_bounds_high(session, skill_factory):
    """Level 100 + success → stays at 100."""
    skill = skill_factory(level=100.0)
    for _ in range(2):
        apply_staircase(session, skill, True, trigger="session_consolidation")
        session.commit()
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()

    assert skill.current_level == 100.0


def test_staircase_none_success(session, skill_factory):
    """None success should record but not move level."""
    skill = skill_factory(level=5.0)
    apply_staircase(session, skill, None, trigger="session_consolidation")
    session.commit()

    assert skill.current_level == 5.0


def test_staircase_history_records_all_fields(session, skill_factory):
    """History should record all fields correctly."""
    skill = skill_factory(level=5.0)
    apply_staircase(session, skill, True, trigger="session_consolidation", session_id=None)
    session.commit()

    history = session.exec(
        select(SkillLevelHistory).where(SkillLevelHistory.skill_id == skill.id)
    ).first()
    assert history is not None
    assert history.success is True
    assert history.level_before == 5.0
    assert history.level_after == 5.0
    assert history.delta == 0.0
    assert history.trigger == "session_consolidation"


# ─── detect_plateau ───────────────────────────────────────────────


def test_plateau_detection(session, skill_factory):
    """5+ sessions with delta=0 → plateau=True."""
    skill = skill_factory(level=5.0)
    # Create a level-up (3 successes) first
    for _ in range(3):
        apply_staircase(session, skill, True, trigger="session_consolidation")
        session.commit()
    # Now create 6 more with success=True — the window of 3 will keep moving
    # but we need the last 5 to have delta=0. After level-up, new window:
    # sessions 4,5 = 2/2 = 100% > 0.67 → move up again
    # sessions 5,6,7 = 3/3 = 100% → move up again
    # sessions 6,7,8 = 3/3 → move up again
    # So we need to create a run where the last 5 don't move.
    # Strategy: after the level-up, create mixed results so the window is at boundary.
    # Actually: just create many sessions where delta=0 (alternating success/fail within window)
    # Simpler: create success=True entries where the window of 3 is always 2/3 = 66.7% → maintain
    # 2/3 = 0.666... < 0.67 → maintains level → delta=0
    for _ in range(6):
        apply_staircase(session, skill, True, trigger="session_consolidation")  # +1 success
        apply_staircase(session, skill, False, trigger="session_consolidation")  # +1 fail
    # Now the last entries should have delta=0 since window of 3 has 2/3 or 1/3 success
    assert detect_plateau(session, skill.id) is True


def test_plateau_no_false_positive(session, skill_factory):
    """Recent level change → plateau=False."""
    skill = skill_factory(level=5.0)
    # Create 4 entries with no level change
    for _ in range(4):
        apply_staircase(session, skill, True, trigger="session_consolidation")
        session.commit()
    # Now force a level change
    for _ in range(2):
        apply_staircase(session, skill, True, trigger="session_consolidation")
        session.commit()
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()

    # After the level-up, check plateau — should be False because
    # the most recent entries include a delta=1
    assert detect_plateau(session, skill.id) is False


def test_plateau_not_enough_data(session, skill_factory):
    """Less than window entries → plateau=False."""
    skill = skill_factory(level=5.0)
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()

    assert detect_plateau(session, skill.id) is False


# ─── compute_practice_level ───────────────────────────────────────


class FakeSession:
    """Minimal mock for practice level testing."""
    def __init__(self, **kwargs):
        self.what_i_practiced = kwargs.get("what_i_practiced", "")
        self.micro_error_found = kwargs.get("micro_error_found", None)
        self.correction_applied = kwargs.get("correction_applied", None)
        self.hypothesis_tomorrow = kwargs.get("hypothesis_tomorrow", None)
        self.difficulty = kwargs.get("difficulty", 3)


def test_practice_level_deliberate():
    """All fields present → deliberate."""
    s = FakeSession(
        what_i_practiced="Practiqué álgebra con foco en ecuaciones cuadráticas",
        micro_error_found="Error de signo en la fórmula",
        correction_applied="Recordar que -b cambia de signo",
        hypothesis_tomorrow="Practicar 5 problemas más con la fórmula",
        difficulty=4,
    )
    assert compute_practice_level(s) == "deliberate"


def test_practice_level_purposeful():
    """Goal + error but no correction → purposeful."""
    s = FakeSession(
        what_i_practiced="Practiqué álgebra con foco en ecuaciones",
        micro_error_found="Error de signo",
        difficulty=3,
    )
    assert compute_practice_level(s) == "purposeful"


def test_practice_level_naive():
    """Short what_i_practiced, no other fields → naive."""
    s = FakeSession(what_i_practiced="Matemáticas")
    assert compute_practice_level(s) == "naive"


def test_practice_level_empty():
    """Empty session → naive."""
    s = FakeSession()
    assert compute_practice_level(s) == "naive"


def test_practice_level_high_difficulty():
    """High difficulty alone → purposeful (1 point from difficulty + 1 from short description = 2)."""
    s = FakeSession(
        what_i_practiced="Practiqué algo difícil hoy",
        difficulty=5,
    )
    assert compute_practice_level(s) == "purposeful"


# ─── determine_session_success ────────────────────────────────────


class FakeGameSession:
    """Minimal mock for game session testing."""
    def __init__(self, skill_id, **kwargs):
        self.skill_id = skill_id
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_determine_session_success_memory_number(session, skill_factory):
    """MemoryNumber: consecutive_correct >= 2 → success."""
    skill = skill_factory(slug="mem-test", skill_type="memory_number")
    gs = FakeGameSession(skill_id=skill.id, consecutive_correct=2, consecutive_incorrect=0)
    assert determine_session_success(session, gs) is True


def test_determine_session_success_memory_number_fail(session, skill_factory):
    """MemoryNumber: consecutive_incorrect >= 2 → failure."""
    skill = skill_factory(slug="mem-test2", skill_type="memory_number")
    gs = FakeGameSession(skill_id=skill.id, consecutive_correct=0, consecutive_incorrect=2)
    assert determine_session_success(session, gs) is False


def test_determine_session_success_math(session, skill_factory):
    """MathThinking: consecutive_correct >= 3 → success."""
    skill = skill_factory(slug="math-test", skill_type="problem_set")
    gs = FakeGameSession(skill_id=skill.id, consecutive_correct=3, consecutive_incorrect=0)
    assert determine_session_success(session, gs) is True


def test_determine_session_success_iq(session, skill_factory):
    """IQPractice: consecutive_correct >= 2 → success."""
    skill = skill_factory(slug="iq-test", skill_type="iq_practice")
    gs = FakeGameSession(skill_id=skill.id, consecutive_correct=2, consecutive_incorrect=0)
    assert determine_session_success(session, gs) is True


def test_determine_session_success_dual_nback(session, skill_factory):
    """DualNBack: tasa_precision > 0.60 → success."""
    skill = skill_factory(slug="dnb-test", skill_type="dual_n_back")
    gs = FakeGameSession(skill_id=skill.id, tasa_precision=0.75)
    assert determine_session_success(session, gs) is True


def test_determine_session_success_dual_nback_fail(session, skill_factory):
    """DualNBack: tasa_precision < 0.40 → failure."""
    skill = skill_factory(slug="dnb-test2", skill_type="dual_n_back")
    gs = FakeGameSession(skill_id=skill.id, tasa_precision=0.30)
    assert determine_session_success(session, gs) is False


def test_determine_session_success_none_when_insufficient(session, skill_factory):
    """MemoryNumber with cc=1, ci=1 → None (mixed, no clear signal)."""
    skill = skill_factory(slug="mem-test3", skill_type="memory_number")
    gs = FakeGameSession(skill_id=skill.id, consecutive_correct=1, consecutive_incorrect=1)
    assert determine_session_success(session, gs) is None


# ─── get_recent_results ───────────────────────────────────────────


def test_get_recent_results_uses_success_field(session, skill_factory):
    """get_recent_results should use the success field, not delta."""
    skill = skill_factory(level=5.0)
    # Create entries: success=True, success=False, success=True
    for s in [True, False, True]:
        apply_staircase(session, skill, s, trigger="session_consolidation")
        session.commit()

    results = get_recent_results(session, skill.id, window=3)
    assert results == [True, False, True]


# ─── Edge case: staircase transition patterns ───────────────────────


def test_staircase_three_successes_levels_up(session, skill_factory):
    """3 consecutive successes after reaching evaluation threshold → level up."""
    skill = skill_factory(level=5.0)
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()
    # 3rd: window=[True, True] + current True → [True, True, True] = 100% ≥ 67% → up
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()
    assert skill.current_level == 6.0


def test_staircase_three_failures_levels_down(session, skill_factory):
    """3 consecutive failures after reaching evaluation threshold → level down."""
    skill = skill_factory(level=5.0)
    apply_staircase(session, skill, False, trigger="session_consolidation")
    session.commit()
    apply_staircase(session, skill, False, trigger="session_consolidation")
    session.commit()
    # 3rd: window=[False, False] + current False → [False, False, False] = 0% ≤ 33% → down
    apply_staircase(session, skill, False, trigger="session_consolidation")
    session.commit()
    assert skill.current_level == 4.0


# ─── Edge case: empty history, single data point ────────────────────


def test_staircase_no_history(session, skill_factory):
    """No history entries → record but no move (already covered by first_session)."""
    skill = skill_factory(level=5.0)
    results = get_recent_results(session, skill.id, window=3)
    assert results == []

    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()
    assert skill.current_level == 5.0


def test_staircase_single_history(session, skill_factory):
    """Exactly 1 history entry → record but no move."""
    skill = skill_factory(level=5.0)
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()

    # 2nd session: window=[True] + current → only 2 total → no move (< 2)
    apply_staircase(session, skill, True, trigger="session_consolidation")
    session.commit()
    assert skill.current_level == 5.0


# ─── Edge case: compute_practice_level extra scenarios ──────────────


def test_practice_level_difficulty_alone_short_text():
    """Difficulty >= 4 with short text → score=1 → naive (short text < 20 chars)."""
    s = FakeSession(
        what_i_practiced="Corto",  # 6 chars, too short
        difficulty=4,
    )
    assert compute_practice_level(s) == "naive"


def test_practice_level_correction_without_goal():
    """Correction without specific goal → purposeful (correction=+1, short text=0...
    wait, micro_error_found=None, correction_applied has a value→+1,
    what_i_practiced is short → total=1? Actually correction_applied and micro_error_found are different.
    """
    s = FakeSession(
        what_i_practiced="Practiqué algo",
        micro_error_found="Some error",
        correction_applied="Fixed it",
        difficulty=2,
    )
    # what_i_practiced is 14 chars (< 20) → no point
    # micro_error_found → +1
    # correction_applied → +1
    # Total = 2 → purposeful
    assert compute_practice_level(s) == "purposeful"


# ─── Edge case: determine_session_success more scenarios ────────────


def test_determine_session_success_no_skill(session):
    """No skill found → returns None."""
    gs = FakeGameSession(skill_id=99999, consecutive_correct=5)
    assert determine_session_success(session, gs) is None


def test_determine_session_success_no_skill_id():
    """No skill_id attribute → returns None."""
    gs = FakeGameSession(skill_id=None)
    # Remove skill_id to simulate missing attribute
    del gs.skill_id
    assert determine_session_success(None, gs) is None


def test_determine_session_success_unknown_type(session, skill_factory):
    """Unknown skill_type → returns None."""
    skill = skill_factory(slug="unknown", skill_type="unknown_type")
    gs = FakeGameSession(skill_id=skill.id, consecutive_correct=5, consecutive_incorrect=0)
    assert determine_session_success(session, gs) is None
