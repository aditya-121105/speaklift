# backend/app/ai/embeddings/__init__.py
"""
Embeddings — Vector Representations
=====================================

Responsible for converting text into dense vector embeddings and
performing semantic similarity operations.

Architecture position
---------------------
Text (string)
    │
    ▼
EmbeddingProvider.embed()     ← this sub-package
    │
    ▼
EmbeddingVector (list[float])
    │
    ├──▶ Vectorizer (batch embedding + storage)
    │
    └──▶ Similarity computation (cosine, dot-product)

Sub-packages
------------
providers/   — Abstract interface + concrete embedding model wrappers.
               Planned: SentenceTransformerProvider (Sprint C.4).
               The existing EmbeddingManager in services/evaluation/embeddings/
               will migrate here.

vectorizers/ — Batch embedding utilities: embed lists of texts, build
               in-memory index, compute top-k neighbours.

services/    — High-level embedding orchestration.
               EmbeddingService provides embed(), similarity(), find_similar().
               Used by the question bank (vector search upgrade), resume
               matcher, and answer evaluation.

Current state
-------------
An EmbeddingManager exists in:
  app/services/evaluation/embeddings/embedding_manager.py

It loads BAAI/bge-base-en-v1.5 via sentence-transformers.
It will be migrated to embeddings/providers/ in Sprint C.4.
The services/evaluation/ version remains in place until then.

Sprint C.2 — package skeleton and abstract provider interface only.
"""
