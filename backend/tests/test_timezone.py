"""
Tests for T-13: datetime.now() → datetime.now(timezone.utc) replacement
and named constant extraction.

Verifies:
- No bare datetime.now() calls without timezone in modified files
- Named constants used in sessions.py for thresholds
- conftest.py session_factory also uses timezone-aware datetime
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone


def test_no_bare_datetime_now_in_models():
    """models/models.py must not contain datetime.now() without timezone."""
    fp = Path(__file__).parent.parent / "models" / "models.py"
    content = fp.read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "datetime.now()" in stripped and "timezone.utc" not in stripped:
            if stripped.startswith("#"):
                continue
            pytest.fail(
                f"models/models.py:{i}: bare datetime.now() found without timezone.utc\n  {stripped}"
            )


def test_no_bare_datetime_now_in_settings():
    """core/settings.py must not contain datetime.now() without timezone."""
    fp = Path(__file__).parent.parent / "core" / "settings.py"
    content = fp.read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "datetime.now()" in stripped and "timezone.utc" not in stripped:
            if stripped.startswith("#"):
                continue
            pytest.fail(
                f"core/settings.py:{i}: bare datetime.now() found without timezone.utc\n  {stripped}"
            )


def test_no_bare_datetime_now_in_sessions():
    """api/routes/sessions.py must not contain datetime.now() without timezone."""
    fp = Path(__file__).parent.parent / "api" / "routes" / "sessions.py"
    content = fp.read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "datetime.now()" in stripped and "timezone.utc" not in stripped:
            if stripped.startswith("#"):
                continue
            pytest.fail(
                f"api/routes/sessions.py:{i}: bare datetime.now() found without timezone.utc\n  {stripped}"
            )


def test_no_bare_datetime_now_in_mental():
    """api/routes/mental.py must not contain datetime.now() without timezone."""
    fp = Path(__file__).parent.parent / "api" / "routes" / "mental.py"
    content = fp.read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "datetime.now()" in stripped and "timezone.utc" not in stripped:
            if stripped.startswith("#"):
                continue
            pytest.fail(
                f"api/routes/mental.py:{i}: bare datetime.now() found without timezone.utc\n  {stripped}"
            )


def test_no_bare_datetime_now_in_conftest():
    """tests/conftest.py must use datetime.now(timezone.utc) in session_factory."""
    fp = Path(__file__).parent.parent / "tests" / "conftest.py"
    content = fp.read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "datetime.now()" in stripped and "timezone.utc" not in stripped:
            if stripped.startswith("#"):
                continue
            pytest.fail(
                f"tests/conftest.py:{i}: bare datetime.now() found without timezone.utc\n  {stripped}"
            )


def test_named_constants_in_sessions():
    """sessions.py must use named constants instead of magic numbers."""
    fp = Path(__file__).parent.parent / "api" / "routes" / "sessions.py"
    content = fp.read_text()
    assert "ONBOARDING_SESSION_THRESHOLD" in content, (
        "ONBOARDING_SESSION_THRESHOLD constant not found in sessions.py"
    )
    assert "MENTALREP_SESSION_THRESHOLD" in content, (
        "MENTALREP_SESSION_THRESHOLD constant not found in sessions.py"
    )


def test_models_use_timezone_utc():
    """Model default factories should produce timezone-aware datetimes."""
    # Verify by importing a model and checking created_at type
    from models.models import Skill, Session, Assessment, MentalRep, Challenge

    skill = Skill(name="tz-test", slug="tz-test", domain="test", skill_type="test", config_path="test")
    assert skill.created_at is not None
    assert skill.created_at.tzinfo is not None, "Skill.created_at must be timezone-aware"
    assert skill.created_at.tzinfo == timezone.utc


def test_timezone_aware_default_factory():
    """datetime.now(timezone.utc) produces the correct UTC time."""
    from datetime import datetime, timezone
    # Verify the pattern itself works
    now = datetime.now(timezone.utc)
    assert now.tzinfo is not None
    assert now.tzinfo == timezone.utc
