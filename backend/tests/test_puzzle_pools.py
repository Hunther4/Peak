"""Tests for the static puzzle pool used at level 1 (IQ + Math).

Covers:
- Pool data is well-formed and verified.
- get_pool_puzzle() rotates without repeating within a session.
- get_pool_puzzle() cycles when all entries have been seen.
- generate_puzzle() / generate_problem() consume the pool for level 1
  and still hit the AI path for level 2+.
- The session tracker has bounded memory.
"""

from types import SimpleNamespace

import pytest

from core.iq_practice import generate_puzzle
from core.math_thinking import generate_problem
from core.puzzle_pools import (
    _MAX_TRACKED_SESSIONS,
    PUZZLE_POOLS,
    _seen_puzzles,
    get_pool_puzzle,
    has_pool,
    reset_all_puzzles,
    reset_session_puzzles,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def _reset_pool_state():
    """Each test starts with an empty seen-set (avoids cross-test pollution)."""
    reset_all_puzzles()
    yield
    reset_all_puzzles()


# =============================================================================
# Data quality tests
# =============================================================================


class TestPoolDataIntegrity:
    """Pool entries must be well-formed and contain the documented fields."""

    def test_iq_pool_has_eight_entries_at_level_1(self):
        """IQ pool has 8 hand-curated entries at level 1."""
        pool = PUZZLE_POOLS["iq_practice"][1]
        assert len(pool) == 8

    def test_math_pool_has_sixteen_entries_at_level_1(self):
        """Math pool has 16 hand-curated entries at level 1 (expanded for static coverage)."""
        pool = PUZZLE_POOLS["problem_set"][1]
        assert len(pool) == 16

    def test_iq_pool_contains_number_sequences_and_verbal_analogies(self):
        """The IQ level-1 pool mixes 4 number_sequence and 4 verbal_analogy."""
        pool = PUZZLE_POOLS["iq_practice"][1]
        types = [p["puzzle_type"] for p in pool]
        assert types.count("number_sequence") == 4
        assert types.count("verbal_analogy") == 4

    @pytest.mark.parametrize("idx", range(8))
    def test_iq_entries_have_required_fields(self, idx):
        """Every IQ entry has question, 4 options, correct_answer in options, source."""
        entry = PUZZLE_POOLS["iq_practice"][1][idx]
        assert "question" in entry and entry["question"]
        assert isinstance(entry["options"], list)
        assert len(entry["options"]) == 4
        for opt in entry["options"]:
            assert isinstance(opt, str) and opt
        assert "correct_answer" in entry
        assert entry["correct_answer"] in entry["options"]
        assert "source" in entry and entry["source"]
        assert "puzzle_type" in entry and entry["puzzle_type"]
        assert "explanation" in entry and entry["explanation"]

    @pytest.mark.parametrize("idx", range(16))
    def test_math_entries_have_numeric_answer_and_steps(self, idx):
        """Math entries carry a finite float answer, steps, question, and source."""
        entry = PUZZLE_POOLS["problem_set"][1][idx]
        assert "question" in entry and entry["question"]
        assert isinstance(entry["correct_answer"], float)
        assert entry["correct_answer"] > 0
        assert isinstance(entry["solution_steps"], list)
        assert len(entry["solution_steps"]) >= 1
        for step in entry["solution_steps"]:
            assert isinstance(step, str) and step
        assert "source" in entry and entry["source"]

    def test_known_fact_math_answers(self):
        """Spot-check the math answers against the known facts in the spec.

        Level 1 problems are daily-life scenarios (shopping, money, food) —
        the math emerges from real situations, not from scientific data.
        See ``core/puzzle_pools.py`` design rule comment.
        """
        # Marker -> expected correct answer (float).
        answer_by_marker = {
            "3 cosas: una remera": 150.0,           # vuelto
            "4 paquetes de yerba": 1_000.0,         # empaque
            "pizza cuesta $1.200": 150.0,          # porción de pizza
            "sin propina": 500.0,                   # cuenta dividida
            "3,5 kilogramos": 3_500.0,             # kilo a gramo
            "1.800 para comprarte": 9.0,            # ahorro mensual
            "30% en comida": 2_500.0,              # presupuesto
            "25% de descuento": 900.0,             # compra con descuento
            "12 huevos": 7.0,                       # huevos en heladera
            "8:15 y tarda 45": 900.0,              # bondi (9:00 como número)
            "2 litros de leche": 1_950.0,           # compra supermercado
            "64 GB": 19.0,                          # almacenamiento libre
            "8 metros de largo": 20.0,              # pared m²
            "3.000 pasos": 5_625.0,                 # actividad física metros
            "10.000 para la semana": 5_000.0,       # presupuesto semanal
            "2,5 tazas de harina": 5.0,             # receta doble
        }
        # Every entry must match exactly one marker and yield the expected answer.
        for entry in PUZZLE_POOLS["problem_set"][1]:
            matches = [
                (m, a) for m, a in answer_by_marker.items()
                if m in entry["question"]
            ]
            assert len(matches) == 1, (
                f"expected exactly 1 marker match, got {matches} "
                f"for question: {entry['question']!r}"
            )
            marker, expected_answer = matches[0]
            assert entry["correct_answer"] == expected_answer, (
                f"question matching {marker!r} returned "
                f"{entry['correct_answer']!r} instead of {expected_answer!r}"
            )

    def test_iq_known_fact_answers_present(self):
        """Spot-check the IQ answers against the known facts in the spec."""
        expected_answers = {
            "40",                          # animales más rápidos
            "8.46 (Makalu)",               # montañas más altas
            "48",                          # progresión ×2
            "2.71828",                     # constante de Euler
            "información",                 # ADN : código genético
            "oración",                     # molécula : célula
            "tejido",                      # galaxia : universo
            "memoria",                     # hipotálamo : temperatura
        }
        actual_answers = {e["correct_answer"] for e in PUZZLE_POOLS["iq_practice"][1]}
        assert expected_answers == actual_answers


# =============================================================================
# Rotation tests
# =============================================================================


class TestPoolRotation:
    """get_pool_puzzle() must not repeat a puzzle within a single session."""

    def test_returns_puzzle_when_pool_exists(self):
        """get_pool_puzzle returns a valid pool entry for level 1."""
        puzzle = get_pool_puzzle("iq_practice", 1, session_id=42)
        assert puzzle is not None
        assert puzzle["correct_answer"] in puzzle["options"]
        assert "source" in puzzle

    def test_returns_none_when_no_pool(self):
        """Levels without a pool return None so the caller falls back to AI."""
        assert get_pool_puzzle("problem_set", 3, session_id=42) is None
        assert get_pool_puzzle("iq_practice", 3, session_id=42) is None
        assert get_pool_puzzle("unknown_skill", 1, session_id=42) is None

    def test_has_pool(self):
        """has_pool() reflects the same lookup."""
        assert has_pool("iq_practice", 1) is True
        assert has_pool("problem_set", 1) is True
        assert has_pool("iq_practice", 2) is True
        assert has_pool("problem_set", 2) is True
        assert has_pool("iq_practice", 3) is False
        assert has_pool("problem_set", 3) is False

    def test_no_repeat_within_a_session(self):
        """All 8 puzzles are returned before any repeats within a session."""
        session_id = 101
        seen_questions = set()
        for _ in range(8):
            puzzle = get_pool_puzzle("iq_practice", 1, session_id=session_id)
            assert puzzle["question"] not in seen_questions, (
                "Puzzle repeated within a single session"
            )
            seen_questions.add(puzzle["question"])
        assert len(seen_questions) == 8

    def test_pool_cycles_after_all_seen(self):
        """After 8 unique puzzles, the seen-set resets and a new round begins."""
        session_id = 202
        first_pass = {
            get_pool_puzzle("iq_practice", 1, session_id=session_id)["question"]
            for _ in range(8)
        }
        assert len(first_pass) == 8

        # 9th call must still return a valid pool entry (the seen-set was
        # cleared, so the pool is once again available in full).
        ninth = get_pool_puzzle("iq_practice", 1, session_id=session_id)
        assert ninth is not None
        # The seen-set should now have exactly 1 entry (just the 9th pick).
        assert len(_seen_puzzles[session_id]) == 1

        # And the next 7 calls must all be unique (cycling restarted cleanly).
        next_seven = {
            get_pool_puzzle("iq_practice", 1, session_id=session_id)["question"]
            for _ in range(7)
        }
        assert len(next_seven) == 7

    def test_different_sessions_track_independently(self):
        """Two sessions can see the same puzzle without affecting each other."""
        p_a = get_pool_puzzle("iq_practice", 1, session_id=301)["question"]
        p_b = get_pool_puzzle("iq_practice", 1, session_id=302)["question"]
        # Both must be valid pool entries; rotation is independent per session.
        pool_questions = {e["question"] for e in PUZZLE_POOLS["iq_practice"][1]}
        assert p_a in pool_questions
        assert p_b in pool_questions

    def test_none_session_id_returns_first_puzzle(self):
        """Without a session_id, the first pool entry is returned (deterministic)."""
        first = PUZZLE_POOLS["iq_practice"][1][0]
        result = get_pool_puzzle("iq_practice", 1, session_id=None)
        # Deep-copied, so identity differs but content matches.
        assert result == first

    def test_reset_session_puzzles_clears_state(self):
        """reset_session_puzzles() makes the full pool available again."""
        session_id = 999
        for _ in range(8):
            get_pool_puzzle("iq_practice", 1, session_id=session_id)
        reset_session_puzzles(session_id)
        # No AssertionError: we can pull all 8 puzzles again.
        questions = {
            get_pool_puzzle("iq_practice", 1, session_id=session_id)["question"]
            for _ in range(8)
        }
        assert len(questions) == 8

    def test_bounded_session_tracker(self):
        """The in-memory session tracker caps at _MAX_TRACKED_SESSIONS."""
        for sid in range(_MAX_TRACKED_SESSIONS + 50):
            get_pool_puzzle("iq_practice", 1, session_id=sid)
        assert len(_seen_puzzles) <= _MAX_TRACKED_SESSIONS


# =============================================================================
# Integration with generate_puzzle / generate_problem
# =============================================================================


class TestGenerateUsesPool:
    """generate_puzzle / generate_problem should consume the pool for level 1."""

    def _make_mock_puzzle(self, label="AI"):
        """Create a mock AI response that should NEVER be returned for level 1."""
        return SimpleNamespace(
            question=f"AI generated question ({label})",
            options=["A", "B", "C", "D"],
            correct_answer="A",
            explanation="AI explanation",
            puzzle_type="number_sequence",
            source="AI source",
        )

    def _make_mock_problem(self, label="AI"):
        return SimpleNamespace(
            question=f"AI generated problem ({label})",
            correct_answer=1.0,
            solution_steps=["AI step"],
            source="AI source",
        )

    def test_generate_puzzle_uses_pool_for_level_1(self):
        """Level 1 should never call the AI router."""
        def router_should_not_be_called(*args, **kwargs):
            raise AssertionError("Router must not be called for level 1 (pool used)")

        result = generate_puzzle(1, {}, router_should_not_be_called, session_id=1)
        pool_questions = {e["question"] for e in PUZZLE_POOLS["iq_practice"][1]}
        assert result["question"] in pool_questions
        assert "source" in result
        assert result["source"] is not None

    def test_generate_problem_uses_pool_for_level_1(self):
        """Level 1 should never call the AI router."""
        def router_should_not_be_called(*args, **kwargs):
            raise AssertionError("Router must not be called for level 1 (pool used)")

        result = generate_problem(1, {}, router_should_not_be_called, session_id=1)
        pool_questions = {e["question"] for e in PUZZLE_POOLS["problem_set"][1]}
        assert result["question"] in pool_questions
        assert "source" in result
        assert result["source"] is not None

    def test_generate_puzzle_falls_back_to_ai_for_level_3(self):
        """For level 3 the AI path is used (no pool for that level)."""
        captured = {}

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            captured["called"] = True
            return self._make_mock_puzzle()

        result = generate_puzzle(3, {}, mock_router, session_id=1)
        assert captured.get("called") is True
        assert result["question"].startswith("AI generated question")

    def test_generate_problem_falls_back_to_ai_for_level_3(self):
        """For level 3 the AI path is used (no pool for that level)."""
        captured = {}

        def mock_router(task_type, system_prompt, user_prompt, response_model):
            captured["called"] = True
            return self._make_mock_problem()

        result = generate_problem(3, {}, mock_router, session_id=1)
        assert captured.get("called") is True
        assert result["question"].startswith("AI generated problem")

    def test_generate_puzzle_rotates_within_session(self):
        """Two calls with the same session_id return different puzzles."""
        def explode(*args, **kwargs):
            raise AssertionError("Should not be called")

        session_id = 555
        a = generate_puzzle(1, {}, explode, session_id=session_id)
        b = generate_puzzle(1, {}, explode, session_id=session_id)
        assert a["question"] != b["question"]

    def test_generate_puzzle_none_session_id_still_uses_pool(self):
        """When session_id is None, level 1 still uses the pool (no rotation)."""
        def explode(*args, **kwargs):
            raise AssertionError("Should not be called")

        result = generate_puzzle(1, {}, explode, session_id=None)
        assert result["question"] == PUZZLE_POOLS["iq_practice"][1][0]["question"]
