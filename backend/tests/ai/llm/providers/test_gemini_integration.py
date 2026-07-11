import os
import pytest
import asyncio
from app.ai.llm.providers.gemini import GeminiProvider
from app.ai.llm.prompts.base import Prompt, PromptVersion
from app.ai.shared.exceptions import LLMProviderError, LLMRateLimitError
from app.core.config import settings

# These tests execute real API calls and are only run when explicitly requested
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not settings.GEMINI_API_KEY,
        reason="GEMINI_API_KEY is required for live integration tests."
    )
]

@pytest.fixture
def provider():
    return GeminiProvider()

@pytest.fixture
def simple_prompt():
    return Prompt(
        name="test",
        version=PromptVersion(major=1, minor=0),
        system_prompt="You are a polite assistant.",
        user_prompt="Say 'Hello Integration Test' exactly."
    )

def test_live_complete(provider, simple_prompt):
    # Tests a real synchronous complete call
    response = provider.complete(simple_prompt, max_tokens=20, temperature=0.0)
    
    assert response is not None
    assert "Hello Integration Test" in response.text
    assert response.provider == "gemini"
    assert response.input_tokens > 0
    assert response.output_tokens > 0

def test_live_stream(provider, simple_prompt):
    # Tests a real synchronous streaming call
    chunks = list(provider.stream(simple_prompt, max_tokens=20, temperature=0.0))
    
    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert "Hello Integration Test" in full_text

def test_live_acomplete(provider, simple_prompt):
    # Tests a real asynchronous complete call
    response = asyncio.run(provider.acomplete(simple_prompt, max_tokens=20, temperature=0.0))
    
    assert response is not None
    assert "Hello Integration Test" in response.text

def test_live_astream(provider, simple_prompt):
    # Tests a real asynchronous streaming call
    async def run_stream():
        chunks = []
        async for chunk in provider.astream(simple_prompt, max_tokens=20, temperature=0.0):
            chunks.append(chunk)
        return chunks
        
    chunks = asyncio.run(run_stream())
    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert "Hello Integration Test" in full_text

def test_live_json_mode(provider):
    json_prompt = Prompt(
        name="test_json",
        version=PromptVersion(major=1, minor=0),
        system_prompt="Return ONLY valid JSON.",
        user_prompt="Output {\"status\": \"ok\"}"
    )
    
    response = provider.complete(json_prompt, json_mode=True, temperature=0.0, max_tokens=20)
    
    # Verify the JSON response
    import json
    parsed = json.loads(response.text)
    assert parsed.get("status") == "ok"
