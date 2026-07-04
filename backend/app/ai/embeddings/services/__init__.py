# backend/app/ai/embeddings/services/__init__.py
"""
Embedding Service
=================

High-level orchestration layer for all embedding operations.

EmbeddingService is the single public entry point for embedding operations
that business services (app/services/) consume. It wraps an EmbeddingProvider
and vectorizer utilities into a cohesive, testable interface.

Planned interface
-----------------
EmbeddingService will expose:

    embed(text: str) -> EmbeddingVector
        Embed a single piece of text. Delegates to EmbeddingProvider.

    embed_batch(texts: list[str]) -> list[EmbeddingVector]
        Embed multiple texts efficiently. Uses provider batch API.

    similarity(a: str, b: str) -> SimilarityScore
        Compute cosine similarity between two texts.
        Embeds both texts and computes their dot product (normalised).

    find_similar(
        query: str,
        candidates: list[str],
        top_k: int = 5,
    ) -> list[tuple[str, SimilarityScore]]
        Return the top-k most semantically similar candidates to the query.
        Used by the question bank (vector search upgrade, Sprint C.4).

Design rules
------------
1. EmbeddingService is the ONLY consumer of EmbeddingProvider in the
   application. Services do not call providers directly.
2. EmbeddingService is injected into callers via FastAPI's dependency
   injection system (app/dependencies/).
3. The underlying EmbeddingProvider is replaceable without changing the
   EmbeddingService interface or its callers.

Migration plan
--------------
The current EmbeddingManager in services/evaluation/embeddings/ will be
replaced by this service in Sprint C.4. Until then both coexist.

Sprint C.2 — skeleton only.
Sprint C.4 — implement EmbeddingService backed by SentenceTransformerProvider.
"""
