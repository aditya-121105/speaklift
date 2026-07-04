# backend/app/ai/embeddings/providers/__init__.py
"""
Embedding Providers
===================

Abstract interface and concrete implementations for embedding model providers.

Design contract
---------------
Every embedding provider must implement EmbeddingProvider. This ensures
the embedding source is pluggable: switching from sentence-transformers
to OpenAI Embeddings, Cohere, or a custom model requires only a new
provider class — no changes to EmbeddingService or its callers.

Planned providers
-----------------
SentenceTransformerProvider  (Sprint C.4)
    Model: BAAI/bge-base-en-v1.5 (768-dim)
    Source: sentence-transformers library (already in pyproject.toml)

OpenAIEmbeddingProvider      (Sprint C.6, optional)
    Model: text-embedding-3-small / text-embedding-3-large
    Source: openai library

Sprint C.2 — abstract interface only.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.shared.types import EmbeddingVector


class EmbeddingProvider(ABC):
    """
    Abstract base class for all embedding model providers.

    An EmbeddingProvider converts text into a dense floating-point vector.
    The vector space is model-specific — vectors from different providers
    MUST NOT be compared directly.

    Design rules
    ------------
    - Providers are SINGLETONS. Each concrete provider is instantiated once
      at application startup and shared via dependency injection.
    - Providers are SYNCHRONOUS. Async wrappers belong in the service layer.
    - Providers raise EmbeddingError (from ai/shared/exceptions.py) on failure.
    - Providers must be STATELESS after initialisation (no per-request state).
    """

    @abstractmethod
    def embed(self, text: str) -> EmbeddingVector:
        """
        Embed a single text string into a dense vector.

        Parameters
        ----------
        text : Input text. Must be non-empty.

        Returns
        -------
        EmbeddingVector — list of floats with length == self.dimension.

        Raises
        ------
        EmbeddingError     — if embedding generation fails.
        AIValidationError  — if text is empty.
        """

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[EmbeddingVector]:
        """
        Embed a batch of text strings.

        Prefer this over repeated embed() calls for performance — most
        transformer models process batches faster than individual sequences.

        Parameters
        ----------
        texts : List of non-empty strings.

        Returns
        -------
        list[EmbeddingVector] — one vector per input text, in the same order.

        Raises
        ------
        EmbeddingError     — if batch embedding fails.
        AIValidationError  — if texts is empty or contains empty strings.
        """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        The output vector dimension for this provider.

        This is a fixed property of the model (e.g. 768 for bge-base-en-v1.5).
        Callers may use this to validate vector stores before inserting.
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Human-readable model identifier for logging and metadata.

        Example: 'BAAI/bge-base-en-v1.5'
        """
