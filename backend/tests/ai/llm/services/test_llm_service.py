import pytest
import asyncio
from unittest.mock import MagicMock
from pydantic import BaseModel

from app.ai.llm.services.llm_service import LLMService
from app.ai.llm.routers.router import LLMRouter
from app.ai.llm.providers import LLMResponse
from app.ai.llm.prompts.base import Prompt, PromptVersion
from app.ai.shared.exceptions import AIValidationError

class MockSchema(BaseModel):
    id: int
    name: str

@pytest.fixture
def mock_router():
    return MagicMock(spec=LLMRouter)

@pytest.fixture
def service(mock_router):
    return LLMService(router=mock_router)

@pytest.fixture
def dummy_prompt():
    return Prompt(
        name="test_service",
        version=PromptVersion(major=1, minor=0),
        user_prompt="Hello"
    )

def test_generate_response(service, mock_router, dummy_prompt):
    mock_response = LLMResponse(text="Test Response", provider="mock")
    mock_router.complete.return_value = mock_response
    
    resp = service.generate_response(dummy_prompt, max_tokens=10, temperature=0.5)
    
    assert resp == mock_response
    mock_router.complete.assert_called_once_with(
        prompt=dummy_prompt,
        max_tokens=10,
        temperature=0.5,
        json_mode=False
    )

def test_generate_text(service, mock_router, dummy_prompt):
    mock_response = LLMResponse(text="Test Text", provider="mock")
    mock_router.complete.return_value = mock_response
    
    text = service.generate_text(dummy_prompt, max_tokens=10, temperature=0.5)
    
    assert text == "Test Text"

def test_generate_json_success_raw(service, mock_router, dummy_prompt):
    raw_json = '{"id": 1, "name": "Alice"}'
    mock_response = LLMResponse(text=raw_json, provider="mock")
    mock_router.complete.return_value = mock_response
    
    result = service.generate_json(dummy_prompt, MockSchema)
    
    assert isinstance(result, MockSchema)
    assert result.id == 1
    assert result.name == "Alice"
    mock_router.complete.assert_called_once_with(
        prompt=dummy_prompt, max_tokens=None, temperature=None, json_mode=True
    )

def test_generate_json_success_markdown(service, mock_router, dummy_prompt):
    md_json = "Here is your output:\n```json\n{\n\"id\": 2,\n\"name\": \"Bob\"\n}\n```\nThank you."
    mock_response = LLMResponse(text=md_json, provider="mock")
    mock_router.complete.return_value = mock_response
    
    result = service.generate_json(dummy_prompt, MockSchema)
    
    assert result.id == 2
    assert result.name == "Bob"

def test_generate_json_success_fallback_extraction(service, mock_router, dummy_prompt):
    dirty_json = "Some prefix... \n  { \"id\": 3, \"name\": \"Charlie\" }  \n ...suffix."
    mock_response = LLMResponse(text=dirty_json, provider="mock")
    mock_router.complete.return_value = mock_response
    
    result = service.generate_json(dummy_prompt, MockSchema)
    
    assert result.id == 3
    assert result.name == "Charlie"

def test_generate_json_decode_error(service, mock_router, dummy_prompt):
    invalid_json = "{ id: 4, name: 'David' }" # Invalid JSON format
    mock_response = LLMResponse(text=invalid_json, provider="mock")
    mock_router.complete.return_value = mock_response
    
    with pytest.raises(AIValidationError, match="Failed to decode LLM JSON response"):
        service.generate_json(dummy_prompt, MockSchema)

def test_generate_json_schema_validation_error(service, mock_router, dummy_prompt):
    bad_schema_json = '{"id": "not_an_int", "name": "Eve"}'
    mock_response = LLMResponse(text=bad_schema_json, provider="mock")
    mock_router.complete.return_value = mock_response
    
    with pytest.raises(AIValidationError, match="LLM JSON validation failed for schema MockSchema"):
        service.generate_json(dummy_prompt, MockSchema)

def test_agenerate_response(service, mock_router, dummy_prompt):
    mock_response = LLMResponse(text="Async Test", provider="mock")
    
    async def mock_acomplete(*args, **kwargs):
        return mock_response
        
    mock_router.acomplete.side_effect = mock_acomplete
    
    resp = asyncio.run(service.agenerate_response(dummy_prompt))
    assert resp == mock_response

def test_agenerate_text(service, mock_router, dummy_prompt):
    mock_response = LLMResponse(text="Async Text", provider="mock")
    
    async def mock_acomplete(*args, **kwargs):
        return mock_response
        
    mock_router.acomplete.side_effect = mock_acomplete
    
    text = asyncio.run(service.agenerate_text(dummy_prompt))
    assert text == "Async Text"

def test_agenerate_json(service, mock_router, dummy_prompt):
    mock_response = LLMResponse(text='{"id": 99, "name": "Zane"}', provider="mock")
    
    async def mock_acomplete(*args, **kwargs):
        return mock_response
        
    mock_router.acomplete.side_effect = mock_acomplete
    
    result = asyncio.run(service.agenerate_json(dummy_prompt, MockSchema))
    assert result.id == 99
    assert result.name == "Zane"
