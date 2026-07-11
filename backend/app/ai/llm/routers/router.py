import logging
from typing import AsyncIterator, Iterator, Sequence

from app.ai.llm.providers import LLMProvider, LLMResponse
from app.ai.llm.prompts.base import Prompt
from app.ai.shared.exceptions import (
    AIConfigurationError,
    AIValidationError,
    LLMProviderError,
    LLMRateLimitError,
    LLMAllProvidersFailedError,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMRouter:
    """
    Provider-agnostic routing layer.
    
    Responsible for executing Prompts against one or more LLM providers
    according to the configured LLM_ROUTING_STRATEGY. Handles fallback
    when providers experience recoverable failures.
    """

    def __init__(self, providers: Sequence[LLMProvider]):
        if not providers:
            raise AIConfigurationError("LLMRouter initialized with empty providers list.")
        self._providers = list(providers)

    def _get_eligible_providers(self) -> list[LLMProvider]:
        strategy = settings.LLM_ROUTING_STRATEGY
        
        local_providers = [p for p in self._providers if p.is_local]
        cloud_providers = [p for p in self._providers if not p.is_local]
        
        if strategy == "prefer_local":
            ordered = local_providers + cloud_providers
        elif strategy == "prefer_cloud":
            ordered = cloud_providers + local_providers
        elif strategy == "local_only":
            ordered = local_providers
        elif strategy == "cloud_only":
            ordered = cloud_providers
        else:
            raise AIConfigurationError(f"Unknown LLM_ROUTING_STRATEGY: {strategy}")
            
        if not ordered:
            raise AIConfigurationError(f"No eligible providers available for strategy: {strategy}")
            
        return ordered

    def _is_recoverable(self, e: Exception) -> bool:
        # Configuration and Validation errors are non-recoverable
        if isinstance(e, (AIConfigurationError, AIValidationError)):
            return False
        # Provider and Rate Limit errors are recoverable
        if isinstance(e, (LLMProviderError, LLMRateLimitError)):
            return True
        # Any other unknown exception is treated as non-recoverable
        return False

    def complete(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        eligible = self._get_eligible_providers()
        
        last_error: Exception | None = None
        for provider in eligible:
            try:
                return provider.complete(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    json_mode=json_mode,
                )
            except Exception as e:
                logger.warning(f"Provider {provider.provider_name} failed: {e}")
                if not self._is_recoverable(e):
                    raise
                last_error = e
                
        raise LLMAllProvidersFailedError(
            f"All providers failed for complete(). Last error: {last_error}"
        ) from last_error

    def stream(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]:
        eligible = self._get_eligible_providers()
        
        last_error: Exception | None = None
        for provider in eligible:
            stream_started = False
            try:
                stream_iter = provider.stream(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                
                try:
                    first_chunk = next(stream_iter)
                except StopIteration:
                    return
                    
                stream_started = True
                yield first_chunk
                yield from stream_iter
                return
                
            except Exception as e:
                if stream_started:
                    # Stream consistency: lock provider after first chunk
                    raise
                logger.warning(f"Provider {provider.provider_name} failed on stream(): {e}")
                if not self._is_recoverable(e):
                    raise
                last_error = e
                
        raise LLMAllProvidersFailedError(
            f"All providers failed for stream(). Last error: {last_error}"
        ) from last_error

    async def acomplete(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        eligible = self._get_eligible_providers()
        
        last_error: Exception | None = None
        for provider in eligible:
            try:
                return await provider.acomplete(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    json_mode=json_mode,
                )
            except Exception as e:
                logger.warning(f"Provider {provider.provider_name} failed on acomplete(): {e}")
                if not self._is_recoverable(e):
                    raise
                last_error = e
                
        raise LLMAllProvidersFailedError(
            f"All providers failed for acomplete(). Last error: {last_error}"
        ) from last_error

    async def astream(
        self,
        prompt: Prompt,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> AsyncIterator[str]:
        eligible = self._get_eligible_providers()
        
        last_error: Exception | None = None
        for provider in eligible:
            stream_started = False
            try:
                stream_iter = provider.astream(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                
                try:
                    first_chunk = await stream_iter.__anext__()
                except StopAsyncIteration:
                    return
                    
                stream_started = True
                yield first_chunk
                async for chunk in stream_iter:
                    yield chunk
                return
                
            except Exception as e:
                if stream_started:
                    # Stream consistency: lock provider after first chunk
                    raise
                logger.warning(f"Provider {provider.provider_name} failed on astream(): {e}")
                if not self._is_recoverable(e):
                    raise
                last_error = e
                
        raise LLMAllProvidersFailedError(
            f"All providers failed for astream(). Last error: {last_error}"
        ) from last_error
