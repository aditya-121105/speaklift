# backend/app/ai/embeddings/vectorizers/__init__.py
"""
Vectorizers
===========

Batch embedding utilities and in-memory vector index operations.

Responsibilities
----------------
- Embed a collection of texts into a matrix of vectors
- Build an in-memory nearest-neighbour index (e.g. FAISS, sklearn NearestNeighbors)
- Compute top-k most similar items given a query vector
- Compute pairwise similarity matrices for small collections

Design rules
------------
- Vectorizers are STATELESS UTILITIES. They accept an EmbeddingProvider
  and raw texts; they return results without storing state.
- Index construction belongs in vectorizers/ but index persistence
  (serialisation to disk) belongs in embeddings/services/.
- Do NOT import business domain objects here. Input is always plain text.

Sprint C.2 — package skeleton only.
"""
