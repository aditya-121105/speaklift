"""
==============================================================================
Module:
    Semantic Similarity Feature Extractor

Milestone:
    M2.1 – Evaluation Engine Completion

Purpose:
    Computes semantic relevance between the interview question and the
    candidate's answer using the locally-cached BAAI/bge-base-en-v1.5
    SentenceTransformer model.

    No external API calls are made. The model is loaded once via
    EmbeddingManager and shared for the application's lifetime.

Strategy
--------
1. Encode both question and answer texts as sentence embeddings.
2. Compute cosine similarity between the two embedding vectors.
3. Clip to [0, 1] for a relevance_score.

Responsibilities:
    ✔ Produce cosine similarity between question and answer
    ✔ Produce normalised relevance_score in [0, 1]
    ✔ Provide human-readable summary

Does NOT:
    ✘ Call external APIs
    ✘ Fine-tune models
    ✘ Access the database
==============================================================================
"""

import math

from app.services.evaluation.embeddings.embedding_manager import EmbeddingManager
from app.services.evaluation.schemas.semantic_evaluation import SemanticEvaluation


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Pure-Python cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class SemanticSimilarityFeatureExtractor:
    """
    Compute embedding-based semantic relevance between a question and an answer.
    """

    def extract(self, question_text: str, answer_text: str) -> SemanticEvaluation:
        if not question_text.strip() or not answer_text.strip():
            return SemanticEvaluation(
                cosine_similarity=0.0,
                relevance_score=0.0,
                summary="Semantic similarity cannot be computed – question or answer is empty.",
            )

        model = EmbeddingManager.get_model()
        embeddings = model.encode(
            [question_text, answer_text],
            normalize_embeddings=True,  # unit-norm for cosine via dot product
        )

        # With normalised vectors, cosine similarity == dot product
        q_vec: list[float] = embeddings[0].tolist()
        a_vec: list[float] = embeddings[1].tolist()
        cosine = _cosine_similarity(q_vec, a_vec)

        # Clip to [0, 1] for relevance_score (negative cosine is not useful here)
        relevance = max(0.0, cosine)

        if relevance >= 0.85:
            label = "Highly Relevant"
        elif relevance >= 0.65:
            label = "Relevant"
        elif relevance >= 0.45:
            label = "Moderately Relevant"
        else:
            label = "Low Relevance"

        summary = (
            f"Semantic relevance: {label} "
            f"(cosine similarity = {cosine:.3f})."
        )

        return SemanticEvaluation(
            cosine_similarity=round(cosine, 6),
            relevance_score=round(relevance, 6),
            summary=summary,
        )
