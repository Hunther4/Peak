import pytest
from core.router import get_ai_mode, set_ai_mode

def test_ai_mode_roundtrip():
    # Test setting to 'api'
    set_ai_mode("api")
    assert get_ai_mode() == "api"
    
    # Test setting to 'local'
    set_ai_mode("local")
    assert get_ai_mode() == "local"
    
    # Test invalid mode (should fallback to 'local')
    set_ai_mode("invalid_mode")
    assert get_ai_mode() == "local"
