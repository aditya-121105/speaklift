# ADR-002: Database Selection

## Status

Accepted

## Context

The platform requires persistent storage for:

* Users
* Interview sessions
* Questions
* Responses
* Evaluations
* Analytics

## Decision

Use PostgreSQL as the primary database.

## Rationale

* Industry standard relational database
* Strong consistency guarantees
* Excellent indexing support
* Powerful analytical queries
* AWS RDS compatibility
* SQLAlchemy support

## Consequences

Positive:

* Strong relational modeling
* Reliable transactions
* Production-ready scalability

Negative:

* More schema planning required than document databases

## Alternatives Considered

### MongoDB

Pros:

* Flexible schema

Cons:

* Less suitable for highly relational interview data

### MySQL

Pros:

* Popular and widely supported

Cons:

* PostgreSQL provides stronger advanced querying capabilities
