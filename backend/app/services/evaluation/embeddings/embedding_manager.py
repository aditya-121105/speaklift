"""
==============================================================================
Module:
    Embedding Manager

Sprint:
    Sprint 4 - Evaluation Engine

Purpose:
    Centralized loader for embedding models.

Responsibilities:
    ✔ Load embedding models once
    ✔ Share models across the application
    ✔ Prevent repeated model initialization

Current Model:
    BAAI/bge-base-en-v1.5

Future Models:
    - Instructor XL
    - Nomic Embed
    - OpenAI Embeddings
    - Gemini Embeddings

==============================================================================
Interview Notes

Q. Why use a singleton manager?

Loading transformer models repeatedly:

- wastes memory
- increases latency
- hurts throughput

A centralized manager loads the model once and shares it across
the application.

==============================================================================
"""

from sentence_transformers import SentenceTransformer


class EmbeddingManager:
    """
    Singleton-style manager for embedding models.
    """

    _embedding_model: SentenceTransformer | None = None

    MODEL_NAME = "BAAI/bge-base-en-v1.5"

    @classmethod
    def get_model(
        cls,
    ) -> SentenceTransformer:
        """
        Return the shared embedding model.
        """

        if cls._embedding_model is None:

            cls._embedding_model = SentenceTransformer(
                cls.MODEL_NAME
            )

        return cls._embedding_model