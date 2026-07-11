import pytest
from unittest.mock import patch

from app.ai.llm.factory import get_llm_service, _reset_llm_service_for_testing
from app.ai.llm.services.llm_service import LLMService
from app.core.config import settings

@pytest.fixture(autouse=True)
def reset_singleton():
    _reset_llm_service_for_testing()
    yield
    _reset_llm_service_for_testing()

def test_singleton_behavior():
    service1 = get_llm_service()
    service2 = get_llm_service()
    
    assert service1 is service2
    assert isinstance(service1, LLMService)

def test_correct_provider_construction_and_injection():
    service = get_llm_service()
    
    # Verify the service has a router
    router = service._router
    assert router is not None
    
    # Verify the router has the correct providers
    providers = router._providers
    assert len(providers) == 2
    
    provider_names = {p.provider_name for p in providers}
    assert "gemini" in provider_names
    assert "ollama" in provider_names

def test_respects_default_provider_configuration(monkeypatch):
    monkeypatch.setattr(settings, "LLM_DEFAULT_PROVIDER", "gemini")
    
    service = get_llm_service()
    router = service._router
    providers = router._providers
    
    # Gemini should be first because it's the default
    assert providers[0].provider_name == "gemini"

def test_respects_different_default_provider(monkeypatch):
    monkeypatch.setattr(settings, "LLM_DEFAULT_PROVIDER", "ollama")
    
    service = get_llm_service()
    router = service._router
    providers = router._providers
    
    # Ollama should be first because it's the default
    assert providers[0].provider_name == "ollama"
