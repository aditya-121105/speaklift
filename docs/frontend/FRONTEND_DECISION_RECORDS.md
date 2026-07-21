# SpeakLift: Frontend Decision Records (ADR) Process

As the Frontend Architecture is now frozen (v1.0), any significant divergence from the established paradigms must be formally documented, reviewed, and approved via an Architecture Decision Record (ADR).

## 1. Purpose of the ADR Process
- **Prevent Architecture Drift**: Ensures the codebase does not organically morph into an unmaintainable state due to disparate developer preferences.
- **Historical Context**: Provides future engineers with the *why* behind a structural choice (e.g., "Why did we switch from Axios to native Fetch?").
- **Knowledge Sharing**: Forces the team to deeply analyze the trade-offs of adopting a new library or design pattern before writing code.

## 2. When is an ADR Required?
An ADR is required when a change affects the global frontend architecture. Examples include:
- Introducing a new core library (e.g., adding `Redux` or `Three.js`).
- Changing the build tooling (e.g., switching from `Webpack` to `Turbopack`).
- Altering the authentication flow.
- Changing the fundamental folder structure (`src/features`).
- Modifying the core design system primitives (changing from Tailwind to CSS-in-JS).

An ADR is **not** required for:
- Building a new feature that adheres to existing folder structures and patterns.
- Refactoring a single component or hook internally without changing its public API.
- Updating dependencies within minor/patch versions.

## 3. Approval Process
1. **Drafting**: An engineer identifies a structural problem and drafts an ADR using the template below.
2. **Review**: The ADR is submitted as a PR to the `docs/frontend/adrs/` directory.
3. **Debate**: The Frontend Architecture team (or Lead) reviews the document, focusing heavily on the "Consequences" section.
4. **Approval**: Once consensus is reached, the PR is merged. The ADR status transitions to "Accepted."
5. **Implementation**: Only after the ADR is merged may the implementation PRs begin.

## 4. Versioning Strategy
- ADRs are stored in `docs/frontend/adrs/`.
- File naming format: `XXXX-short-title.md` (e.g., `0001-adopt-tanstack-query.md`).
- ADR numbers are sequential and never reused.
- If an ADR is superseded by a later decision, its status is updated to "Superseded," but the file is never deleted.

---

## Appendix: ADR Template

```markdown
# ADR 00XX: [Short, descriptive title]

**Date:** YYYY-MM-DD
**Status:** [Proposed | Accepted | Rejected | Superseded by 00XY]

## Context
What is the problem we are trying to solve? Why does the current architecture fail to address it? What is the business or technical motivation for this change?

## Decision
What is the specific architectural change we are making? (e.g., "We will migrate all data fetching from Axios to native fetch() wrapped in custom Web Streams.")

## Trade-offs Considered
What were the alternatives? Why were they rejected? (e.g., "Alternative 1: Keep Axios. Rejected because it does not natively support Edge streaming.")

## Consequences
What becomes easier? What becomes harder? What existing code needs to be rewritten? (e.g., "Positive: Faster time-to-first-byte on AI generation. Negative: We must manually rewrite our error normalization interceptors.")
```
