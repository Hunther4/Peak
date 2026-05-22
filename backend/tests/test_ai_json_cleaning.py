import pytest
from pydantic import BaseModel
from core.utils import clean_json_response, parse_structured_json

class MockModel(BaseModel):
    name: str
    value: int

def test_markdown_wrapper_cleanup():
    # Case 1: Standard markdown block
    content = 'Here is the result:\n```json\n{"name": "test", "value": 123}\n```'
    cleaned = clean_json_response(content)
    assert cleaned == '{"name": "test", "value": 123}'
    
    # Case 2: Markdown block without 'json' identifier
    content = '```\n{"name": "test", "value": 123}\n```'
    cleaned = clean_json_response(content)
    assert cleaned == '{"name": "test", "value": 123}'
    
    # Case 3: Just "json" prefix
    content = 'json\n{"name": "test", "value": 123}'
    cleaned = clean_json_response(content)
    assert cleaned == '{"name": "test", "value": 123}'
    
    # Case 4: Text before and after JSON
    content = 'Some text before {\"name\": \"test\", \"value\": 123} some text after'
    cleaned = clean_json_response(content)
    assert cleaned == '{"name": "test", "value": 123}'

def test_invalid_json_returns_none():
    # Completely invalid JSON
    content = 'This is not JSON at all'
    result = parse_structured_json(content, MockModel)
    assert result is None
    
    # Partially valid but wrong schema
    content = '{"wrong_key": "wrong_value"}'
    result = parse_structured_json(content, MockModel)
    assert result is None
    
    # Empty content
    content = ''
    result = parse_structured_json(content, MockModel)
    assert result is None
