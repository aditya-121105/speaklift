import pytest
import asyncio

from app.ai.llm.routers.router import LLMRouter
from app.ai.llm.providers import LLMProvider, LLMResponse
from app.ai.shared.exceptions import (
    AIConfigurationError,
    AIValidationError,
    LLMProviderError,
    LLMAllProvidersFailedError,
)
from app.ai.llm.prompts.base import Prompt, PromptVersion
from app.core.config import settings

class MockProvider(LLMProvider):
    def __init__(self, name: str, is_local_flag: bool):
        self._name = name
        self._is_local = is_local_flag
        self.should_fail = False
        self.error_to_raise = None
        self.responses = []

    @property
    def provider_name(self) -> str: return self._name
    @property
    def model_name(self) -> str: return "mock"
    @property
    def supports_json_mode(self) -> bool: return True
    @property
    def supports_function_calling(self) -> bool: return False
    @property
    def supports_streaming(self) -> bool: return True
    @property
    def context_window(self) -> int: return 1000
    @property
    def is_local(self) -> bool: return self._is_local

    def _maybe_fail(self):
        if self.should_fail:
            raise self.error_to_raise or LLMProviderError(f"{self._name} failed")

    def complete(self, prompt, **kwargs):
        self._maybe_fail()
        self.responses.append(prompt)
        return LLMResponse(text=f"Response from {self._name}", provider=self._name)

    def stream(self, prompt, **kwargs):
        self._maybe_fail()
        self.responses.append(prompt)
        yield f"Chunk 1 from {self._name}"
        self._maybe_fail() # can fail mid-stream if configured to do so at an exact step, but we will use a separate flag for mid-stream
        yield f"Chunk 2 from {self._name}"

    async def acomplete(self, prompt, **kwargs):
        self._maybe_fail()
        self.responses.append(prompt)
        return LLMResponse(text=f"Async Response from {self._name}", provider=self._name)

    async def astream(self, prompt, **kwargs):
        self._maybe_fail()
        self.responses.append(prompt)
        yield f"Async Chunk 1 from {self._name}"
        yield f"Async Chunk 2 from {self._name}"

class MidStreamFailProvider(MockProvider):
    def stream(self, prompt, **kwargs):
        self.responses.append(prompt)
        yield f"Chunk 1 from {self._name}"
        raise LLMProviderError(f"Mid-stream crash in {self._name}")

    async def astream(self, prompt, **kwargs):
        self.responses.append(prompt)
        yield f"Async Chunk 1 from {self._name}"
        raise LLMProviderError(f"Mid-stream crash in {self._name}")


@pytest.fixture
def local_prov():
    return MockProvider("mock_local", True)

@pytest.fixture
def cloud_prov():
    return MockProvider("mock_cloud", False)

@pytest.fixture
def dummy_prompt():
    return Prompt(
        name="test",
        version=PromptVersion(major=1, minor=0),
        user_prompt="Hello"
    )

def test_router_initialization_empty_list():
    with pytest.raises(AIConfigurationError):
        LLMRouter([])

def test_get_eligible_providers(local_prov, cloud_prov, monkeypatch):
    router = LLMRouter([cloud_prov, local_prov])
    
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    assert [p.provider_name for p in router._get_eligible_providers()] == ["mock_local", "mock_cloud"]

    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_cloud")
    assert [p.provider_name for p in router._get_eligible_providers()] == ["mock_cloud", "mock_local"]

    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "local_only")
    assert [p.provider_name for p in router._get_eligible_providers()] == ["mock_local"]

    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "cloud_only")
    assert [p.provider_name for p in router._get_eligible_providers()] == ["mock_cloud"]

def test_routing_success_first_try(local_prov, cloud_prov, dummy_prompt, monkeypatch):
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    router = LLMRouter([local_prov, cloud_prov])
    
    response = router.complete(dummy_prompt)
    assert response.provider == "mock_local"
    assert len(local_prov.responses) == 1
    assert len(cloud_prov.responses) == 0

def test_fallback_on_recoverable_error(local_prov, cloud_prov, dummy_prompt, monkeypatch):
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    local_prov.should_fail = True
    
    router = LLMRouter([local_prov, cloud_prov])
    response = router.complete(dummy_prompt)
    
    assert response.provider == "mock_cloud"
    assert len(local_prov.responses) == 0
    assert len(cloud_prov.responses) == 1

def test_all_providers_failed(local_prov, cloud_prov, dummy_prompt, monkeypatch):
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    local_prov.should_fail = True
    cloud_prov.should_fail = True
    
    router = LLMRouter([local_prov, cloud_prov])
    
    with pytest.raises(LLMAllProvidersFailedError):
        router.complete(dummy_prompt)

def test_non_recoverable_error_aborts_immediately(local_prov, cloud_prov, dummy_prompt, monkeypatch):
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    local_prov.should_fail = True
    local_prov.error_to_raise = AIValidationError("Bad prompt")
    
    router = LLMRouter([local_prov, cloud_prov])
    
    with pytest.raises(AIValidationError):
        router.complete(dummy_prompt)
    
    assert len(cloud_prov.responses) == 0

def test_stream_routing_success(local_prov, cloud_prov, dummy_prompt, monkeypatch):
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    router = LLMRouter([local_prov, cloud_prov])
    
    chunks = list(router.stream(dummy_prompt))
    assert len(chunks) == 2
    assert "mock_local" in chunks[0]

def test_stream_fallback_before_first_chunk(local_prov, cloud_prov, dummy_prompt, monkeypatch):
    # Tests that fallback correctly happens if provider fails BEFORE any chunks
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    local_prov.should_fail = True
    
    router = LLMRouter([local_prov, cloud_prov])
    chunks = list(router.stream(dummy_prompt))
    
    assert len(chunks) == 2
    assert "mock_cloud" in chunks[0]

def test_no_stream_fallback_mid_stream(cloud_prov, dummy_prompt, monkeypatch):
    # Tests that mid-stream exception immediately bubbles up and stops fallback loop
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    
    crashing_prov = MidStreamFailProvider("crasher", True)
    router = LLMRouter([crashing_prov, cloud_prov])
    
    stream_iter = router.stream(dummy_prompt)
    
    # First chunk succeeds
    chunk1 = next(stream_iter)
    assert chunk1 == "Chunk 1 from crasher"
    
    # Second chunk throws, should NOT fallback
    with pytest.raises(LLMProviderError, match="Mid-stream crash in crasher"):
        next(stream_iter)
        
    assert len(cloud_prov.responses) == 0

def test_async_routing_success(local_prov, cloud_prov, dummy_prompt, monkeypatch):
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    router = LLMRouter([local_prov, cloud_prov])
    
    resp = asyncio.run(router.acomplete(dummy_prompt))
    assert resp.provider == "mock_local"

def test_async_stream_fallback_before_first_chunk(local_prov, cloud_prov, dummy_prompt, monkeypatch):
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    local_prov.should_fail = True
    
    router = LLMRouter([local_prov, cloud_prov])
    
    async def run_stream():
        return [c async for c in router.astream(dummy_prompt)]
        
    chunks = asyncio.run(run_stream())
    assert len(chunks) == 2
    assert "mock_cloud" in chunks[0]

def test_no_async_stream_fallback_mid_stream(cloud_prov, dummy_prompt, monkeypatch):
    monkeypatch.setattr(settings, "LLM_ROUTING_STRATEGY", "prefer_local")
    
    crashing_prov = MidStreamFailProvider("async_crasher", True)
    router = LLMRouter([crashing_prov, cloud_prov])
    
    async def run_failing_stream():
        chunks = []
        async_iter = router.astream(dummy_prompt)
        chunks.append(await async_iter.__anext__())
        await async_iter.__anext__() # This should raise
        
    with pytest.raises(LLMProviderError, match="Mid-stream crash in async_crasher"):
        asyncio.run(run_failing_stream())
        
    assert len(cloud_prov.responses) == 0
