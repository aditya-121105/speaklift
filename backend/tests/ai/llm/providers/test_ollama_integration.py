import pytest
import asyncio
import httpx

from app.ai.llm.providers.ollama import OllamaProvider
from app.ai.llm.prompts.base import Prompt, PromptVersion
from app.core.config import settings

OLLAMA_AVAILABLE = False
try:
    with httpx.Client(timeout=1.0) as client:
        response = client.get(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags")
        if response.status_code == 200:
            OLLAMA_AVAILABLE = True
except Exception:
    pass

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not OLLAMA_AVAILABLE,
        reason=f"Ollama server not reachable at {settings.OLLAMA_BASE_URL}"
    )
]

@pytest.fixture
def provider():
    return OllamaProvider()

@pytest.fixture
def simple_prompt():
    return Prompt(
        name="test_ollama",
        version=PromptVersion(major=1, minor=0),
        system_prompt="You are a helpful assistant.",
        user_prompt="Say 'Ollama Integration' exactly."
    )

def test_live_complete(provider, simple_prompt):
    response = provider.complete(simple_prompt, max_tokens=20, temperature=0.0)
    
    assert response is not None
    assert "Integration" in response.text
    assert response.provider == "ollama"
    assert response.model == settings.OLLAMA_DEFAULT_MODEL
    assert response.input_tokens > 0
    assert response.output_tokens > 0

def test_live_stream(provider, simple_prompt):
    chunks = list(provider.stream(simple_prompt, max_tokens=20, temperature=0.0))
    
    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert "Integration" in full_text

def test_live_acomplete(provider, simple_prompt):
    response = asyncio.run(provider.acomplete(simple_prompt, max_tokens=20, temperature=0.0))
    
    assert response is not None
    assert "Integration" in response.text

def test_live_astream(provider, simple_prompt):
    async def run_stream():
        chunks = []
        async for chunk in provider.astream(simple_prompt, max_tokens=20, temperature=0.0):
            chunks.append(chunk)
        return chunks
        
    chunks = asyncio.run(run_stream())
    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert "Integration" in full_text

def test_live_json_mode(provider):
    json_prompt = Prompt(
        name="test_json",
        version=PromptVersion(major=1, minor=0),
        system_prompt="Return ONLY valid JSON.",
        user_prompt="Output {\"status\": \"ok\"}"
    )
    
    response = provider.complete(json_prompt, json_mode=True, temperature=0.0, max_tokens=20)
    
    import json
    try:
        parsed = json.loads(response.text)
        assert parsed.get("status") == "ok"
    except json.JSONDecodeError:
        pytest.fail(f"Ollama did not return valid JSON: {response.text}")
