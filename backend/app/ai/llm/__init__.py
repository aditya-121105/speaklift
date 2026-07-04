# backend/app/ai/llm/__init__.py
"""
LLM — Large Language Model Orchestration
==========================================

Responsible for all interaction with Large Language Model providers.

Architecture position
---------------------
Business Service (e.g. InterviewService)
    │
    ▼
LLMService  ← this sub-package
    │  (selects provider, applies prompt, handles routing + fallback)
    ├──▶ LLMRouter          ← provider selection and fallback logic
    │        │
    │        ▼
    │    LLMProvider ABC    ← implemented by each concrete provider
    │        │
    │        ├── GeminiProvider     (Sprint C.5)
    │        ├── OllamaProvider     (Sprint C.5)
    │        └── OpenAIProvider     (Sprint C.6, optional)
    │
    └──▶ PromptTemplate     ← structured prompt construction

Engineering philosophy
----------------------
SpeakLift is NOT an LLM wrapper. LLMs are used only for tasks where
simpler approaches are demonstrably insufficient (generative question
creation, free-text feedback synthesis). See AI_ENGINEERING_GUIDE.md §1.

Design rules
------------
1. All LLM calls go through LLMService — never directly from endpoints
   or business services.
2. LLMService is the only caller of LLMProvider.
3. Providers are pluggable: switching or adding a provider requires no
   changes to LLMService or its callers.
4. Prompt construction is isolated in prompts/ — service code must not
   build prompt strings inline.
5. Routing and fallback logic lives in routers/ — it is NOT inside any
   provider implementation.

Sub-packages
------------
providers/   — LLMProvider ABC + concrete provider implementations.
               Sprint C.2: abstract interface only.
               Sprint C.5: GeminiProvider, OllamaProvider.

prompts/     — PromptTemplate system. Typed, versioned prompt builders
               for each use case (question generation, feedback, etc.).
               Sprint C.2: skeleton only.
               Sprint C.5: implement PromptTemplate base + first templates.

routers/     — Provider selection and fallback chain.
               Sprint C.2: skeleton only.
               Sprint C.5: implement PriorityRouter with retry + fallback.

services/    — LLMService: the single public entry point for all LLM calls.
               Sprint C.2: skeleton only.
               Sprint C.5: implement LLMService.

Cost and latency strategy
--------------------------
See AI_ENGINEERING_GUIDE.md §7 (Cost Optimization Strategy).
Primary: local Ollama (free, low latency on-device).
Fallback: Gemini Flash (cheap, fast API).
Reserve: GPT-4o / Gemini Pro (high-quality, used sparingly).

Sprint history
--------------
C.2 (2026-07-04) — Package skeleton created. LLMProvider ABC defined.
                   No provider implementations.
C.5             — Implement GeminiProvider, OllamaProvider, LLMRouter,
                   LLMService, and first PromptTemplates.
"""
