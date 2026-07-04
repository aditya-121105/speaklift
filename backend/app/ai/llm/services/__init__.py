# backend/app/ai/llm/services/__init__.py
"""
LLM Service
===========

The single public entry point for all LLM interactions in SpeakLift.

Design contract
---------------
LLMService is the ONLY module that business services (app/services/) may
import from the llm/ sub-package. Business services must not import
LLMProvider, LLMRouter, or PromptTemplate directly.

This single-entry-point rule means:
- Provider selection is invisible to callers.
- Prompt versioning is transparent to callers.
- Routing and fallback are transparent to callers.
- Cost tracking is centralised.

Planned interface
-----------------
LLMService will expose:

    generate(use_case: str, variables: dict) -> LLMResponse
        The primary method. Selects a PromptTemplate by use_case,
        renders it with variables, routes to the best available provider,
        and returns the response.

    stream(use_case: str, variables: dict) -> Iterator[str]
        Streaming variant. Returns a generator of text chunks.

    generate_json(use_case: str, variables: dict, schema: type) -> BaseModel
        Structured output variant. Returns a validated Pydantic model.

Dependency injection
--------------------
LLMService receives its LLMRouter via constructor injection.
LLMRouter receives its list of LLMProviders via constructor injection.
This allows full test isolation (mock providers in tests).

Sprint C.2 — skeleton only.
Sprint C.5 — implement LLMService with all three methods above.
"""
