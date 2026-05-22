"""
Tests for the Memory Number Skill feature.

Covers:
- Unit tests for core.memory_number (generate_numbers, calculate_staircase, evaluate_attempt)
- Integration tests for the /api/memory-game endpoints via TestClient
"""
import pytest
import json
from core.memory_number import (
    generate_numbers,
    calculate_staircase,
    evaluate_attempt,
    get_phase_config,
    PHASES,
)


# =============================================================================
# Unit Tests — generate_numbers()
# =============================================================================

class TestGenerateNumbers:
    """Number generation with correct count and range per phase."""

    def test_phase_1_span_4_returns_4_numbers(self):
        """span=4 produces exactly 4 numbers."""
        nums = generate_numbers(4, 1)
        assert len(nums) == 4

    def test_phase_1_span_5_returns_5_numbers(self):
        """span=5 produces exactly 5 numbers."""
        nums = generate_numbers(5, 1)
        assert len(nums) == 5

    def test_phase_1_span_7_returns_7_numbers(self):
        """span=7 produces exactly 7 numbers."""
        nums = generate_numbers(7, 1)
        assert len(nums) == 7

    def test_phase_1_numbers_are_single_digit(self):
        """Phase 1 (digit_max=1) produces numbers 0-9."""
        nums = generate_numbers(20, 1)
        assert all(0 <= n <= 9 for n in nums)

    def test_phase_3_numbers_are_two_digits(self):
        """Phase 3 (digit_max=2) produces numbers 0-99."""
        nums = generate_numbers(20, 2)
        assert all(0 <= n <= 99 for n in nums)

    def test_phase_5_numbers_are_three_digits(self):
        """Phase 5 (digit_max=3) produces numbers 0-999."""
        nums = generate_numbers(20, 3)
        assert all(0 <= n <= 999 for n in nums)

    def test_ai_assisted_produces_variable_lengths(self):
        """Phase 7 (ai_assisted=True) produces numbers with variable digit lengths."""
        nums = generate_numbers(30, 9, ai_assisted=True)
        # With 30 numbers and random digit lengths 1-4, at least some should
        # be > 9 (2+ digits) and at least some should be <= 9 (1 digit)
        assert len(nums) == 30
        has_single = any(0 <= n <= 9 for n in nums)
        has_multi = any(n >= 10 for n in nums)
        assert has_single, "Expected at least one single-digit number with ai_assisted"
        assert has_multi, "Expected at least one multi-digit number with ai_assisted"

    def test_ai_assisted_all_numbers_in_0_to_9999(self):
        """Phase 7 numbers stay within 0..9999 (10^4 - 1)."""
        nums = generate_numbers(50, 9, ai_assisted=True)
        assert all(0 <= n <= 9999 for n in nums), "ai_assisted numbers must be 0-9999"


# =============================================================================
# Unit Tests — calculate_staircase()
# =============================================================================

class TestCalculateStaircase:
    """Staircase algorithm: span progression, phase changes, floor/ceiling."""

    def test_three_correct_at_span_5_increases_span(self):
        """3 correct at span 5 → span becomes 6."""
        result = calculate_staircase(
            current_span=5, phase=1,
            was_correct=True, consecutive_correct=2, consecutive_incorrect=0,
        )
        assert result["new_span"] == 6
        assert result["new_consecutive_correct"] == 0  # reset after advancing
        assert result["phase_changed"] is False
        assert result["new_phase"] == 1
        assert "3" in result["message"]

    def test_three_correct_at_span_7_advances_phase(self):
        """3 correct at span 7 (phase 1 max) → advances to phase 2, span=8."""
        result = calculate_staircase(
            current_span=7, phase=1,
            was_correct=True, consecutive_correct=2, consecutive_incorrect=0,
        )
        assert result["phase_changed"] is True
        assert result["new_phase"] == 2
        assert result["new_span"] == 8  # phase 2 min_span
        assert "Avanzaste" in result["message"]

    def test_one_incorrect_resets_consecutive(self):
        """1 error → consecutive_correct resets, consecutive_incorrect increments."""
        result = calculate_staircase(
            current_span=5, phase=1,
            was_correct=False, consecutive_correct=2, consecutive_incorrect=0,
        )
        assert result["new_consecutive_correct"] == 0
        assert result["new_consecutive_incorrect"] == 1
        assert result["new_span"] == 5  # span stays same
        assert "Incorrecto" in result["message"]

    def test_three_incorrect_at_same_span_decreases_span(self):
        """3 consecutive incorrect → span -= 2."""
        result = calculate_staircase(
            current_span=6, phase=1,
            was_correct=False, consecutive_correct=0, consecutive_incorrect=2,
        )
        assert result["new_span"] == 4
        assert result["new_consecutive_incorrect"] == 0  # reset after adjustment
        assert result["phase_changed"] is False
        assert "3 errores" in result["message"]

    def test_three_incorrect_at_phase_1_min_span_stays_at_floor(self):
        """3 incorrect at min_span (4) in phase 1 → span stays at 4 (floor)."""
        result = calculate_staircase(
            current_span=4, phase=1,
            was_correct=False, consecutive_correct=0, consecutive_incorrect=2,
        )
        assert result["new_span"] == 4, "Span should not go below min_span for phase 1"
        assert result["phase_changed"] is False
        assert result["new_phase"] == 1

    def test_three_incorrect_in_phase_2_regresses_to_phase_1(self):
        """3 incorrect at phase 2 with span dropping below min → regress to phase 1."""
        # Phase 2 min is 8, so at span=9, 3 incorrect → 9-2=7 which is < 8
        result = calculate_staircase(
            current_span=9, phase=2,
            was_correct=False, consecutive_correct=0, consecutive_incorrect=2,
        )
        assert result["phase_changed"] is True
        assert result["new_phase"] == 1
        assert result["new_span"] == 7  # phase 1 max_span
        assert "retrocedes" in result["message"]

    def test_one_correct_less_than_3_keeps_span(self):
        """Correct but not yet 3 consecutive → span stays same."""
        result = calculate_staircase(
            current_span=5, phase=1,
            was_correct=True, consecutive_correct=1, consecutive_incorrect=0,
        )
        assert result["new_span"] == 5
        assert result["new_consecutive_correct"] == 2
        assert result["phase_changed"] is False
        assert "Correcto" in result["message"]

    def test_max_phase_cap_at_phase_7(self):
        """At phase 7 max_span, 3 correct stays at max_span with message."""
        result = calculate_staircase(
            current_span=80, phase=7,
            was_correct=True, consecutive_correct=2, consecutive_incorrect=0,
        )
        assert result["new_span"] == 80  # max_span for phase 7
        assert result["phase_changed"] is False
        assert result["new_phase"] == 7
        assert "techo" in result["message"]


# =============================================================================
# Unit Tests — evaluate_attempt()
# =============================================================================

class TestEvaluateAttempt:
    """Position-by-position evaluation of recall attempts."""

    def test_all_correct(self):
        """All numbers match → correct=True, correct_positions=total."""
        expected = [3, 7, 1, 9]
        result = evaluate_attempt(expected, [3, 7, 1, 9])
        assert result["correct"] is True
        assert result["correct_positions"] == 4
        assert result["total_positions"] == 4
        assert result["errors"] == []

    def test_some_wrong(self):
        """Some wrong → correct=False, errors list has entries."""
        expected = [3, 7, 1, 9]
        submitted = [3, 5, 1, 9]
        result = evaluate_attempt(expected, submitted)
        assert result["correct"] is False
        assert result["correct_positions"] == 3
        assert len(result["errors"]) == 1
        assert result["errors"][0] == {"position": 1, "expected": 7, "got": 5}

    def test_all_wrong(self):
        """All wrong → correct=False, correct_positions=0."""
        expected = [3, 7, 1, 9]
        submitted = [0, 0, 0, 0]
        result = evaluate_attempt(expected, submitted)
        assert result["correct"] is False
        assert result["correct_positions"] == 0
        assert len(result["errors"]) == 4

    def test_fewer_submitted_than_expected(self):
        """Fewer submitted → attempt marked incorrect."""
        expected = [3, 7, 1, 9]
        submitted = [3, 7]
        result = evaluate_attempt(expected, submitted)
        assert result["correct"] is False
        assert result["correct_positions"] == 0 # Now invalidates completely

    def test_more_submitted_than_expected(self):
        """More submitted → attempt marked incorrect."""
        expected = [3, 7, 1]
        submitted = [3, 7, 1, 9, 5]
        result = evaluate_attempt(expected, submitted)
        assert result["correct"] is False
        assert result["correct_positions"] == 0
        assert len(result["errors"]) == 1
        assert result["errors"][0]["position"] == -1


# =============================================================================
# Integration Tests — POST /api/memory-game/sessions
# =============================================================================

class TestCreateGameSession:
    """POST /api/memory-game/sessions"""

    def test_creates_session_with_correct_structure(self, client, skill_factory):
        """Creates a game session and returns expected fields."""
        skill = skill_factory(skill_type="memory_number")
        response = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["phase"] == 1
        assert data["current_span"] == 4
        assert data["best_span"] == 4
        assert data["best_phase"] == 1
        assert "timing" in data
        assert data["timing"] == 5  # phase 1 timing


# =============================================================================
# Integration Tests — POST /api/memory-game/sessions/{id}/rounds
# =============================================================================

class TestCreateRound:
    """POST /api/memory-game/sessions/{id}/rounds"""

    def test_creates_round_with_numbers(self, client, skill_factory):
        """Creates a round with numbers matching session span/phase."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]

        response = client.post(f"/api/memory-game/sessions/{session_id}/rounds")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["phase"] == 1
        assert data["span"] == 4
        assert data["length"] == 4
        assert data["timing"] == 5
        assert "numbers" in data
        assert len(data["numbers"]) == 4
        # Phase 1 numbers are single digit
        assert all(0 <= n <= 9 for n in data["numbers"])

    def test_returns_404_for_nonexistent_session(self, client):
        """Non-existent session ID returns 404."""
        response = client.post("/api/memory-game/sessions/99999/rounds")
        assert response.status_code == 404

    def test_returns_400_for_inactive_session(self, client, skill_factory):
        """Consolidated (inactive) session returns 400."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]

        # Create 3 rounds
        for _ in range(3):
            client.post(f"/api/memory-game/sessions/{session_id}/rounds")

        # Consolidate to make inactive
        client.post(f"/api/memory-game/sessions/{session_id}/consolidate")

        # Now try to add a round
        response = client.post(f"/api/memory-game/sessions/{session_id}/rounds")
        assert response.status_code == 400
        assert "closed" in response.json()["detail"].lower()


# =============================================================================
# Integration Tests — POST /api/memory-game/rounds/{id}/attempts
# =============================================================================

class TestSubmitAttempt:
    """POST /api/memory-game/rounds/{id}/attempts"""

    def test_correct_submission(self, client, skill_factory):
        """Correct submission returns correct=True, errors=[]."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]
        round_resp = client.post(f"/api/memory-game/sessions/{session_id}/rounds")
        round_data = round_resp.json()
        round_id = round_data["id"]

        # Submit the exact numbers back
        response = client.post(
            f"/api/memory-game/rounds/{round_id}/attempts",
            json={"submitted_numbers": round_data["numbers"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["correct"] is True
        assert data["errors"] == []
        assert data["correct_positions"] == data["total_positions"]

    def test_wrong_submission(self, client, skill_factory):
        """Wrong submission returns correct=False, errors with position details."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]
        round_resp = client.post(f"/api/memory-game/sessions/{session_id}/rounds")
        round_data = round_resp.json()
        round_id = round_data["id"]

        # Submit all zeros — likely wrong
        wrong = [0] * round_data["length"]
        response = client.post(
            f"/api/memory-game/rounds/{round_id}/attempts",
            json={"submitted_numbers": wrong},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["correct"] is False
        assert len(data["errors"]) > 0
        assert data["correct_positions"] < data["total_positions"]

    def test_updates_staircase_on_correct(self, client, skill_factory):
        """3 correct attempts advance the span."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]

        # Submit 3 correct attempts
        for _ in range(3):
            round_resp = client.post(f"/api/memory-game/sessions/{session_id}/rounds")
            round_data = round_resp.json()
            client.post(
                f"/api/memory-game/rounds/{round_data['id']}/attempts",
                json={"submitted_numbers": round_data["numbers"]},
            )

        # Check session state — span should have increased
        state_resp = client.get(f"/api/memory-game/sessions/{session_id}/state")
        state = state_resp.json()
        assert state["current_span"] >= 5, "Expected span to increase after 3 correct"
        assert state["total_rounds"] == 3

    def test_updates_staircase_on_wrong(self, client, skill_factory):
        """Wrong attempts increase consecutive_incorrect."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]

        # Submit 2 wrong attempts
        for _ in range(2):
            round_resp = client.post(f"/api/memory-game/sessions/{session_id}/rounds")
            round_data = round_resp.json()
            wrong = [999] * round_data["length"]  # Almost certainly wrong
            client.post(
                f"/api/memory-game/rounds/{round_data['id']}/attempts",
                json={"submitted_numbers": wrong},
            )

        state_resp = client.get(f"/api/memory-game/sessions/{session_id}/state")
        state = state_resp.json()
        assert state["consecutive_incorrect"] == 2
        assert state["consecutive_correct"] == 0

    def test_returns_404_for_nonexistent_round(self, client):
        """Non-existent round returns 404."""
        response = client.post(
            "/api/memory-game/rounds/99999/attempts",
            json={"submitted_numbers": [1, 2, 3, 4]},
        )
        assert response.status_code == 404


# =============================================================================
# Integration Tests — POST /api/memory-game/sessions/{id}/consolidate
# =============================================================================

class TestConsolidateSession:
    """POST /api/memory-game/sessions/{id}/consolidate"""

    def test_returns_400_if_less_than_3_rounds(self, client, skill_factory):
        """Consolidation requires at least 3 rounds."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]

        # Only 1 round
        client.post(f"/api/memory-game/sessions/{session_id}/rounds")

        response = client.post(f"/api/memory-game/sessions/{session_id}/consolidate")
        assert response.status_code == 400
        assert "Minimum 3 rounds" in response.json()["detail"]

    def test_consolidates_and_creates_practice_session(self, client, skill_factory):
        """Successful consolidation creates a PracticeSession."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]

        # Create 3 rounds
        for _ in range(3):
            client.post(f"/api/memory-game/sessions/{session_id}/rounds")

        response = client.post(f"/api/memory-game/sessions/{session_id}/consolidate")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "consolidated"
        assert "practice_session_id" in data
        assert data["rounds_completed"] == 3

        # Verify the PracticeSession exists
        from models.models import Session as PracticeSession
        from core.database import engine
        from sqlmodel import Session as DBSession
        with DBSession(engine) as db:
            ps = db.get(PracticeSession, data["practice_session_id"])
            assert ps is not None
            assert ps.skill_id == skill.id
            assert ps.duration_minutes >= 10

    def test_returns_400_if_already_consolidated(self, client, skill_factory):
        """Already consolidated session returns 400."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]

        # Create 3 rounds and consolidate
        for _ in range(3):
            client.post(f"/api/memory-game/sessions/{session_id}/rounds")
        client.post(f"/api/memory-game/sessions/{session_id}/consolidate")

        # Try again
        response = client.post(f"/api/memory-game/sessions/{session_id}/consolidate")
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_returns_404_for_nonexistent_session(self, client):
        """Non-existent session returns 404."""
        response = client.post("/api/memory-game/sessions/99999/consolidate")
        assert response.status_code == 404


# =============================================================================
# Integration Tests — GET /api/memory-game/sessions/{id}/state
# =============================================================================

class TestGetGameState:
    """GET /api/memory-game/sessions/{id}/state"""

    def test_returns_session_state(self, client, skill_factory):
        """Returns current game session state."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]

        response = client.get(f"/api/memory-game/sessions/{session_id}/state")
        assert response.status_code == 200
        data = response.json()
        assert data["phase"] == 1
        assert data["current_span"] == 4
        assert data["is_active"] is True
        assert data["total_rounds"] == 0
        assert "timing" in data

    def test_returns_404_for_nonexistent_session(self, client):
        """Non-existent session returns 404."""
        response = client.get("/api/memory-game/sessions/99999/state")
        assert response.status_code == 404


# =============================================================================
# Integration Tests — GET /api/memory-game/sessions/{id}/history
# =============================================================================

class TestGetHistory:
    """GET /api/memory-game/sessions/{id}/history"""

    def test_returns_round_history(self, client, skill_factory):
        """Returns rounds with attempt data."""
        skill = skill_factory(skill_type="memory_number")
        session_resp = client.post("/api/memory-game/sessions", params={"skill_id": skill.id})
        session_id = session_resp.json()["id"]

        # Create a round and submit an attempt
        round_resp = client.post(f"/api/memory-game/sessions/{session_id}/rounds")
        round_data = round_resp.json()
        client.post(
            f"/api/memory-game/rounds/{round_data['id']}/attempts",
            json={"submitted_numbers": round_data["numbers"]},
        )

        response = client.get(f"/api/memory-game/sessions/{session_id}/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["rounds"]) == 1
        assert data["rounds"][0]["id"] == round_data["id"]
        assert data["rounds"][0]["correct"] is True
