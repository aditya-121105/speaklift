# ADR-004: Modular Monolith Architecture

## Status

Accepted

## Context

The platform includes multiple domains:

* Authentication
* Interviews
* Viva
* Evaluation
* Analytics
* Speech
* Vision

The team is small and development speed is important.

## Decision

Use a Modular Monolith architecture.

## Rationale

A modular monolith provides:

* Clear module boundaries
* Easier development
* Easier debugging
* Easier deployment
* Lower operational overhead

while preserving the ability to migrate selected modules into microservices later.

## Future Extraction Candidates

* Speech Service
* Vision Service
* Evaluation Service

## Consequences

Positive:

* Faster development
* Lower infrastructure complexity

Negative:

* Less independent scaling than true microservices

## Alternatives Considered

### Microservices

Pros:

* Independent deployment
* Independent scaling

Cons:

* Higher complexity
* Higher operational cost
* Overkill for initial project stage

