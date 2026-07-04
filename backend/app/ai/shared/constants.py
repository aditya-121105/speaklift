# backend/app/ai/shared/constants.py
"""
AI Shared Constants
===================

Global constants shared across all AI sub-packages.

Design rules
------------
- Only primitive constants (strings, ints, floats). No imports of domain objects.
- Sub-package-specific constants (e.g. NLP model names, LLM token limits)
  belong in that sub-package's own constants file, not here.
- No business logic.

Sprint C.2 — structure only.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Confidence thresholds
# ---------------------------------------------------------------------------

#: Minimum confidence required for an AI result to be considered reliable.
#: Results below this threshold should be flagged for human review.
MIN_RELIABLE_CONFIDENCE: float = 0.60

#: High-confidence threshold — results at or above this require no review.
HIGH_CONFIDENCE_THRESHOLD: float = 0.85

#: Minimum cosine similarity for two embeddings to be considered semantically
#: related. Below this value they are treated as unrelated.
MIN_SEMANTIC_SIMILARITY: float = 0.50

#: Cosine similarity threshold for considering two items duplicates.
DUPLICATE_SIMILARITY_THRESHOLD: float = 0.95


# ---------------------------------------------------------------------------
# Embedding dimensions
# ---------------------------------------------------------------------------

#: Output dimension of BAAI/bge-base-en-v1.5 (the configured embedding model).
BGE_BASE_EMBEDDING_DIM: int = 768

#: Output dimension of all-MiniLM-L6-v2 (lightweight fallback).
MINILM_EMBEDDING_DIM: int = 384


# ---------------------------------------------------------------------------
# Document processing
# ---------------------------------------------------------------------------

#: Maximum number of characters to process in a single document.
#: Documents exceeding this are chunked before processing.
MAX_DOCUMENT_CHARS: int = 100_000

#: Maximum number of tokens a spaCy pipeline will process per call.
#: Aligns with en_core_web_sm defaults.
MAX_SPACY_TOKENS: int = 1_000_000


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

#: Default maximum tokens for LLM completions.
DEFAULT_LLM_MAX_TOKENS: int = 1024

#: Default temperature for LLM generation (balanced creativity / consistency).
DEFAULT_LLM_TEMPERATURE: float = 0.7

#: Number of retry attempts before failing over to the next LLM provider.
LLM_MAX_RETRIES: int = 3

#: Maximum number of fallback providers to try before raising
#: LLMAllProvidersFailedError.
LLM_MAX_PROVIDER_ATTEMPTS: int = 3
