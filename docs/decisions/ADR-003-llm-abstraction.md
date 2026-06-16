# ADR-003: LLM Provider Abstraction Layer

## Status

Accepted

## Context

The platform depends on Large Language Models for:

* Question generation
* Follow-up question generation
* Answer evaluation
* Feedback generation

Directly coupling business logic to a single provider creates vendor lock-in.

## Decision

Introduce an LLM Provider Abstraction Layer.

## Rationale

The application will communicate through a common interface rather than directly calling provider SDKs.

Supported providers:

* Ollama
* OpenAI
* Gemini
* Claude

## Benefits

* Avoid vendor lock-in
* Easier testing
* Easier provider switching
* Lower operational risk
* Better architecture

## Example Interface

* generate_question()
* evaluate_answer()
* generate_feedback()

## Consequences

Positive:

* Flexible architecture
* Easier future migration

Negative:

* Slightly more implementation complexity
