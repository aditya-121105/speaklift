# backend/app/ai/shared/types.py
"""
AI Shared Types
===============

Primitive type aliases and Pydantic base models used across all AI
sub-packages.

Design rules
------------
- All types here must be generic and reusable across sub-packages.
- Domain-specific types (e.g. ResumeContent, InterviewContext) belong
  inside the sub-package that owns them, not here.
- No business logic. No implementations. Definitions only.

Sprint C.2 — structure only.
"""

from __future__ import annotations


from pydantic import BaseModel, ConfigDict, JsonValue


# ---------------------------------------------------------------------------
# Primitive aliases
# ---------------------------------------------------------------------------

#: A raw confidence score in [0.0, 1.0].
ConfidenceScore = float

#: A floating-point similarity score, typically in [-1.0, 1.0] or [0.0, 1.0]
#: depending on the metric (cosine vs dot-product).
SimilarityScore = float

#: A dense embedding vector (list of floats produced by a sentence transformer).
EmbeddingVector = list[float]

#: A JSON-serializable value (string, number, boolean, None, or nested lists/dicts of these).
JSONValue = JsonValue

#: Provider-agnostic key-value metadata attached to AI artefacts.
AIMetadata = dict[str, JSONValue]


# ---------------------------------------------------------------------------
# Base classes
# ---------------------------------------------------------------------------

class AIResult(BaseModel):
    """
    Base class for all AI output objects.

    Every concrete result type (DocumentContent, ExtractionResult,
    EvaluationScore, etc.) should inherit from this class so that
    callers can handle them generically.

    Fields
    ------
    confidence : Overall confidence of the result in [0.0, 1.0].
                 1.0 = fully deterministic (rule-based), 0.0 = no signal.
    metadata   : Arbitrary key-value pairs for debugging, provenance, or
                 pipeline tracing. Not for business logic.
    """

    model_config = ConfigDict(frozen=True)

    confidence: ConfidenceScore = 1.0
    metadata: AIMetadata = {}


class AIRequest(BaseModel):
    """
    Base class for all AI input objects.

    Concrete request types (DocumentExtractionRequest, etc.) extend this.
    """

    model_config = ConfigDict(frozen=True)
