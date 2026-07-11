from app.ai.llm.providers.gemini import GeminiProvider
from app.ai.llm.providers.ollama import OllamaProvider
from app.ai.llm.routers.router import LLMRouter
from app.ai.llm.services.llm_service import LLMService
from app.core.config import settings

_llm_service_instance: LLMService | None = None

def get_llm_service() -> LLMService:
    """
    Composition root for the AI subsystem.
    
    Instantiates concrete providers, configures the router according to
    settings, and wires the dependencies into a singleton LLMService.
    """
    global _llm_service_instance
    
    if _llm_service_instance is None:
        # 1. Instantiate concrete providers
        providers = [OllamaProvider(), GeminiProvider()]
        
        # 2. Respect LLM_DEFAULT_PROVIDER by prioritizing it
        # This prevents hardcoding the order while allowing configuration control
        default_name = settings.LLM_DEFAULT_PROVIDER.lower()
        
        ordered_providers = []
        for p in providers:
            if p.provider_name.lower() == default_name:
                ordered_providers.insert(0, p)
            else:
                ordered_providers.append(p)
                
        # 3. Inject providers into the router
        router = LLMRouter(providers=ordered_providers)
        
        # 4. Inject router into the service
        _llm_service_instance = LLMService(router=router)
        
    return _llm_service_instance

def _reset_llm_service_for_testing():
    """Testing utility to reset the singleton state."""
    global _llm_service_instance
    _llm_service_instance = None
