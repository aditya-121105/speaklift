# backend/app/ai/llm/providers/__init__.py
"""
LLM Providers
=============

Abstract interface for all Large Language Model provider implementations.

Design contract
---------------
Every concrete LLM provider (Gemini, Ollama, OpenAI, Cohere, etc.) MUST:
  1. Inherit from LLMProvider.
  2. Implement all abstract methods.
  3. Raise LLMProviderError on non-retryable failures.
  4. Raise LLMRateLimitError on HTTP 429 / quota-exceeded responses.
  5. Be STATELESS after initialisation (no per-request mutable state).
  6. Be registered with LLMRouter (llm/routers/) for fallback chaining.

Providers must NOT be called directly from business services.
All calls go through LLMService (llm/services/).

Planned providers
-----------------
OllamaProvider    (Sprint C.5) — local inference, zero API cost, primary
GeminiProvider    (Sprint C.5) — Google Gemini Flash, cheap fallback
OpenAIProvider    (Sprint C.6, optional) — GPT-4o, high-quality reserve

Sprint C.2 — abstract interface only. No provider implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterator

from app.ai.shared.types import AIMetadata


class LLMResponse:
    """
    Typed response object returned by LLMProvider.complete().

    Attributes
    ----------
    text           : The generated completion text.
    input_tokens   : Number of tokens in the prompt (for cost tracking).
    output_tokens  : Number of tokens in the completion (for cost tracking).
    model          : Model identifier used for this specific call
                     (may differ from the provider's default if overridden).
    provider       : Name of the provider that produced this response.
    metadata       : Provider-specific extras (finish reason, logprobs, etc.).
                     Not for business logic.
    """

    __slots__ = (
        "text",
        "input_tokens",
        "output_tokens",
        "model",
        "provider",
        "metadata",
    )

    def __init__(
        self,
        text: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        model: str = "",
        provider: str = "",
        metadata: AIMetadata | None = None,
    ) -> None:
        self.text = text
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.model = model
        self.provider = provider
        self.metadata: AIMetadata = metadata or {}


class LLMProvider(ABC):
    """
    Abstract base class for all LLM provider implementations.

    An LLMProvider encapsulates the API interaction for a single
    LLM backend. It is responsible for:
    - Sending prompt strings to the underlying API.
    - Returning structured LLMResponse objects.
    - Surfacing provider-specific capabilities (JSON mode, function calling).
    - Raising the correct AI exceptions on failures.

    It is NOT responsible for:
    - Prompt construction (that belongs in llm/prompts/).
    - Routing or fallback (that belongs in llm/routers/).
    - Business logic of any kind.

    Threading
    ---------
    Providers are shared singletons. All methods must be safe to call
    concurrently from multiple request threads/coroutines. Use no mutable
    instance state after __init__.
    """

    # ------------------------------------------------------------------
    # Core completion methods
    # ------------------------------------------------------------------

    @abstractmethod
    def complete(
        self,
        prompt: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        Send a prompt and return a complete (non-streaming) response.

        Parameters
        ----------
        prompt        : The user-facing prompt string.
        max_tokens    : Maximum number of tokens to generate.
                        Defaults to the provider's configured limit.
        temperature   : Sampling temperature in [0.0, 2.0].
                        Defaults to the provider's configured temperature.
        system_prompt : Optional system/instruction prefix.
                        If None, the provider's default system prompt applies.
        json_mode     : If True, instruct the model to return valid JSON.
                        Only valid if self.supports_json_mode is True.

        Returns
        -------
        LLMResponse — the generated text and token usage.

        Raises
        ------
        LLMProviderError      — non-retryable API failure.
        LLMRateLimitError     — rate limit or quota exceeded (retryable).
        AIValidationError     — prompt is empty or json_mode requested but
                                not supported by this provider.
        AIConfigurationError  — provider not correctly initialised.
        """

    @abstractmethod
    def stream(
        self,
        prompt: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
    ) -> Iterator[str]:
        """
        Send a prompt and yield response tokens as they arrive (streaming).

        Parameters
        ----------
        prompt        : The user-facing prompt string.
        max_tokens    : Maximum number of tokens to generate.
        temperature   : Sampling temperature in [0.0, 2.0].
        system_prompt : Optional system/instruction prefix.

        Yields
        ------
        str — successive text chunks as they are received from the API.

        Raises
        ------
        LLMProviderError      — non-retryable streaming failure.
        LLMRateLimitError     — rate limit exceeded.
        AIConfigurationError  — provider not correctly initialised.

        Note
        ----
        Implementations that do not support streaming should raise
        NotImplementedError. LLMRouter will fall back to complete().
        """

    @abstractmethod
    async def acomplete(
        self,
        prompt: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        Async variant of complete(). Required for FastAPI endpoint use.

        Same contract as complete() with identical parameters and
        exception semantics. Providers that have no native async SDK
        should run complete() in a thread pool executor.
        """

    @abstractmethod
    async def astream(
        self,
        prompt: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """
        Async streaming variant. Yields text chunks asynchronously.

        Same contract as stream() but using async generator semantics
        for use with FastAPI StreamingResponse.
        """

    # ------------------------------------------------------------------
    # Provider capability flags
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Stable identifier for this provider implementation.

        Used by LLMRouter for logging, metrics, and fallback decisions.
        Must be unique across all registered providers.

        Example: 'ollama', 'gemini', 'openai'
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Specific model identifier used by this provider instance.

        Example: 'gemini-1.5-flash', 'llama3.1:8b', 'gpt-4o'
        """

    @property
    @abstractmethod
    def supports_json_mode(self) -> bool:
        """
        True if this provider can be instructed to return valid JSON.

        When False, callers must parse JSON from free-text output and
        handle parse errors. When True, the provider guarantees valid
        JSON on success (though content may still be semantically wrong).
        """

    @property
    @abstractmethod
    def supports_function_calling(self) -> bool:
        """
        True if this provider supports structured function/tool calling.

        When True, the provider can return structured tool invocations
        that callers can parse without regex. When False, the service
        layer must use prompt engineering to extract structured data.
        """

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """
        True if this provider natively supports token-by-token streaming.

        When False, LLMRouter will not route streaming requests to this
        provider and will fall back to a streaming-capable one.
        """

    @property
    @abstractmethod
    def context_window(self) -> int:
        """
        Maximum number of tokens (prompt + completion) this provider accepts.

        LLMRouter uses this to avoid sending oversized prompts to a provider
        and route to a larger-context alternative instead.

        Example: 8192 (Ollama llama3.1:8b), 1_000_000 (Gemini 1.5 Pro)
        """
