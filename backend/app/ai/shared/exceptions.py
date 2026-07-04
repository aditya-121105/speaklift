# backend/app/ai/shared/exceptions.py
"""
AI Shared Exceptions
====================

Exception hierarchy for all AI operations.

All AI exceptions inherit from AIException so that service-layer callers
can catch them with a single handler.

Design rules
------------
- These exceptions represent AI pipeline failures, NOT HTTP errors.
- The service layer translates AIExceptions into HTTP responses via the
  global exception handler in app/core/exception_handlers.py.
- No business logic. Definitions only.

Hierarchy
---------
AIException (base)
├── AIConfigurationError    — missing model, invalid provider config
├── AIProcessingError       — pipeline failure during processing
│   ├── DocumentExtractionError
│   ├── NLPProcessingError
│   ├── EmbeddingError
│   └── LLMError
│       ├── LLMProviderError
│       ├── LLMRateLimitError
│       └── LLMAllProvidersFailedError
├── AIValidationError       — invalid input to an AI component
└── AIResourceNotAvailableError  — model/resource not loaded

Sprint C.2 — structure only.
"""

from __future__ import annotations


class AIException(Exception):
    """Base exception for all AI pipeline errors."""

    def __init__(self, message: str = "An AI error occurred") -> None:
        self.message = message
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


# ---------------------------------------------------------------------------
# Configuration errors
# ---------------------------------------------------------------------------

class AIConfigurationError(AIException):
    """
    Raised when an AI component is misconfigured.

    Examples
    --------
    - Required environment variable missing (API key, model name)
    - Unsupported provider specified in settings
    - Model weights file not found at startup
    """


# ---------------------------------------------------------------------------
# Processing errors
# ---------------------------------------------------------------------------

class AIProcessingError(AIException):
    """
    Raised when an AI pipeline step fails during execution.

    Concrete sub-classes narrow the failure to a specific pipeline stage.
    """


class DocumentExtractionError(AIProcessingError):
    """
    Raised when a document cannot be extracted or parsed.

    Examples
    --------
    - Corrupted PDF bytes
    - Unsupported file format passed to extractor
    - Text layer missing from scanned PDF
    """


class NLPProcessingError(AIProcessingError):
    """
    Raised when an NLP pipeline step fails.

    Examples
    --------
    - spaCy model not loaded
    - Token limit exceeded
    - Entity recognition produces no output on non-empty input
    """


class EmbeddingError(AIProcessingError):
    """
    Raised when vector embedding generation fails.

    Examples
    --------
    - Sentence-transformer model not loaded
    - Empty input sequence passed to encoder
    - Embedding dimension mismatch
    """


class LLMError(AIProcessingError):
    """Base class for all LLM provider errors."""


class LLMProviderError(LLMError):
    """
    Raised when an LLM provider API call fails.

    Examples
    --------
    - HTTP 5xx from provider
    - Malformed response body
    - Authentication failure
    """


class LLMRateLimitError(LLMError):
    """
    Raised when an LLM provider returns HTTP 429 (rate limit exceeded).

    The router should catch this and fall back to the next provider.
    """


class LLMAllProvidersFailedError(LLMError):
    """
    Raised when all configured LLM providers are unavailable.

    This is a terminal error — the caller should return a graceful
    degradation response rather than retrying immediately.
    """


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

class AIValidationError(AIException):
    """
    Raised when AI component receives invalid or unsupported input.

    Examples
    --------
    - Empty document passed to extractor
    - Negative confidence threshold
    - Embedding vector with wrong dimensions
    """


# ---------------------------------------------------------------------------
# Resource availability errors
# ---------------------------------------------------------------------------

class AIResourceNotAvailableError(AIException):
    """
    Raised when a required AI resource (model, index, cache) is not loaded.

    This typically indicates a startup failure or lazy-loading not yet
    triggered. Should trigger an alert in production monitoring.
    """
