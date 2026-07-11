import pytest
import asyncio
from unittest.mock import patch

from app.ai.llm.providers.gemini import GeminiProvider
from app.ai.llm.providers import LLMResponse
from app.ai.shared.exceptions import AIConfigurationError, AIValidationError
from app.ai.llm.prompts.base import Prompt, PromptRenderResult, PromptVersion
from app.core.config import settings

@pytest.fixture
def provider():
    return GeminiProvider()

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    return monkeypatch

@pytest.fixture
def valid_prompt():
    return Prompt(
        name="test",
        version=PromptVersion(major=1, minor=0),
        system_prompt="You are a bot.",
        user_prompt="Say hi."
    )

def test_provider_properties(provider):
    assert provider.provider_name == "gemini"
    assert provider.supports_json_mode is True
    assert provider.supports_function_calling is True
    assert provider.supports_streaming is True
    assert provider.context_window == 1_000_000

def test_missing_api_key_raises_configuration_error(provider, valid_prompt, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)
    
    with pytest.raises(AIConfigurationError, match="GEMINI_API_KEY is not configured"):
        provider.complete(valid_prompt)

def test_empty_prompt_raises_validation_error(provider, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "fake-key")
    
    empty_prompt = Prompt(
        name="empty",
        version=PromptVersion(major=1, minor=0),
        user_prompt="   "
    )
    
    with pytest.raises(AIValidationError, match="Prompt user text cannot be empty"):
        provider.complete(empty_prompt)

def test_rejects_raw_string(provider, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "fake-key")
    
    with pytest.raises(AIValidationError, match="GeminiProvider requires exactly a Prompt aggregate"):
        provider.complete("Hello")

def test_rejects_prompt_render_result(provider, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "fake-key")
    
    render_result = PromptRenderResult(system_prompt="Sys", user_prompt="User")
    with pytest.raises(AIValidationError, match="GeminiProvider requires exactly a Prompt aggregate"):
        provider.complete(render_result)

def test_complete_with_prompt_object(provider, valid_prompt, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(settings, "LLM_TEMPERATURE", 0.7)
    monkeypatch.setattr(settings, "LLM_MAX_OUTPUT_TOKENS", 2048)
    
    mock_response = LLMResponse(text="Hi", provider="gemini")
    
    with patch.object(provider, "_execute_complete", return_value=mock_response) as mock_exec:
        resp = provider.complete(valid_prompt, json_mode=True, temperature=0.9, max_tokens=500)
        
        assert resp == mock_response
        mock_exec.assert_called_once_with("You are a bot.", "Say hi.", 0.9, 500, True)

def test_acomplete(provider, valid_prompt, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "fake-key")
    
    mock_response = LLMResponse(text="Async", provider="gemini")
    
    with patch.object(provider, "_execute_acomplete", return_value=mock_response) as mock_exec:
        resp = asyncio.run(provider.acomplete(valid_prompt))
        
        assert resp == mock_response
        mock_exec.assert_called_once()
