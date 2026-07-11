import pytest
import asyncio
from unittest.mock import patch, MagicMock

from app.ai.llm.providers.ollama import OllamaProvider
from app.ai.llm.providers import LLMResponse
from app.ai.shared.exceptions import AIValidationError, LLMProviderError
from app.ai.llm.prompts.base import Prompt, PromptRenderResult, PromptVersion
from app.core.config import settings
import ollama
import httpx

@pytest.fixture
def provider():
    return OllamaProvider()

@pytest.fixture
def valid_prompt():
    return Prompt(
        name="test_ollama",
        version=PromptVersion(major=1, minor=0),
        system_prompt="You are an Ollama bot.",
        user_prompt="Say local hi."
    )

def test_provider_properties(provider):
    assert provider.provider_name == "ollama"
    assert provider.supports_json_mode is True
    assert provider.supports_function_calling is False
    assert provider.supports_streaming is True
    assert provider.model_name == settings.OLLAMA_DEFAULT_MODEL

def test_empty_prompt_raises_validation_error(provider):
    empty_prompt = Prompt(
        name="empty",
        version=PromptVersion(major=1, minor=0),
        user_prompt="   "
    )
    with pytest.raises(AIValidationError, match="Prompt user text cannot be empty"):
        provider.complete(empty_prompt)

def test_rejects_raw_string(provider):
    with pytest.raises(AIValidationError, match="OllamaProvider requires exactly a Prompt aggregate"):
        provider.complete("Hello")

def test_complete_with_prompt_object(provider, valid_prompt):
    mock_response = LLMResponse(text="Local Hi", provider="ollama")
    
    with patch.object(provider, "_execute_complete", return_value=mock_response) as mock_exec:
        resp = provider.complete(valid_prompt, json_mode=True, temperature=0.5, max_tokens=256)
        
        assert resp == mock_response
        mock_exec.assert_called_once_with("You are an Ollama bot.", "Say local hi.", 0.5, 256, True)

def test_acomplete(provider, valid_prompt):
    mock_response = LLMResponse(text="Async Local Hi", provider="ollama")
    
    with patch.object(provider, "_execute_acomplete", return_value=mock_response) as mock_exec:
        resp = asyncio.run(provider.acomplete(valid_prompt))
        
        assert resp == mock_response
        mock_exec.assert_called_once()

def test_handle_api_error_translation(provider):
    req_err = httpx.RequestError("Connection refused")
    handled_req_err = provider._handle_api_error(req_err)
    assert isinstance(handled_req_err, LLMProviderError)
    assert "connection error" in str(handled_req_err).lower()

    resp_err = ollama.ResponseError("Model not found", status_code=404)
    handled_resp_err = provider._handle_api_error(resp_err)
    assert isinstance(handled_resp_err, LLMProviderError)
    assert "404" in str(handled_resp_err)
