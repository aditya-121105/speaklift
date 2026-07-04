# backend/app/ai/llm/routers/__init__.py
"""
LLM Router — Provider Selection and Fallback
=============================================

Responsible for selecting which LLMProvider handles each request,
and for orchestrating retries and fallback across providers.

Routing strategy
----------------
The router implements a PRIORITY CHAIN:

  1. Primary: OllamaProvider (local, zero cost, lowest latency)
  2. Fallback 1: GeminiFlashProvider (cheap, fast, reliable API)
  3. Fallback 2: GeminiProProvider (higher quality, used sparingly)
  4. Reserve: OpenAIProvider (optional, highest cost)

The router selects a provider based on:
  - Provider availability (health check / recent failure state)
  - Request requirements (json_mode, function_calling, streaming, context_window)
  - Cost preference (prefer local first)

Fallback triggers
-----------------
- LLMRateLimitError       → move to next provider immediately
- LLMProviderError        → retry current provider (up to LLM_MAX_RETRIES),
                            then move to next provider
- LLMAllProvidersFailedError → raised when all providers fail

Design rules
------------
1. The router is the ONLY caller of LLMProvider methods.
2. Routing logic must NOT be scattered across services or providers.
3. Fallback decisions are based on exception type only — not on response content.
4. The router maintains a lightweight failure window (circuit-breaker pattern)
   so a recently-failed provider is temporarily skipped without repeated hits.
5. Cost accounting (token counts) is aggregated here for observability.

Sprint C.2 — skeleton only. No routing logic implemented.
Sprint C.5 — implement PriorityRouter with circuit-breaker and cost tracking.
"""
