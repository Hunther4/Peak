import pytest
from sqlmodel import Session
from core.settings import get_setting, set_setting
from models.models import AppSetting

def test_set_get_roundtrip(session):
    """T-09: set/get roundtrip"""
    key = "test_key"
    value = "test_value"
    
    set_setting(key, value)
    result = get_setting(key)
    
    assert result == value

def test_get_nonexistent_returns_default():
    """T-10: nonexistent key returns default"""
    key = "nonexistent_key"
    default = "my_default"
    
    result = get_setting(key, default=default)
    
    assert result == default
