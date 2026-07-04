# backend/app/ai/ranking/__init__.py
"""
AI Ranking
==========

Responsible for ranking algorithms that order candidates, questions,
or content items by relevance or quality.

Ranking problems in SpeakLift
------------------------------
1. Question Ranking (Sprint C.4)
      Rank question bank entries by match quality against a candidate profile.
      Current approach: metadata keyword matching (skills, technologies arrays).
      Upgrade path: embedding cosine similarity → BM25 → learned ranking.

2. Candidate Ranking (Sprint C.5)
      Rank candidates against a job description by profile similarity.
      Approach: embedding similarity + ML-scored feature vector composite.

3. Recommendation Ranking (Sprint C.6)
      Order improvement recommendations by expected impact.
      Approach: rule-based heuristics first, ML ranking if insufficient.

Architecture rule
-----------------
Ranking is STATELESS and CONTEXT-FREE — rankers receive a query and a
list of candidates and return a sorted result. They have no knowledge of
the business domain beyond what is in their inputs. Domain context is
resolved by the service layer BEFORE calling the ranker.

Planned components
------------------
SimilarityRanker    (Sprint C.4)
    — Ranks items by cosine similarity to a query embedding.
    — Used for vector search upgrade of the question bank.

CompositeRanker     (Sprint C.5)
    — Combines multiple similarity signals (embedding + metadata) into a
    — single ranked list using weighted scoring.

Sprint C.2 — skeleton only.
Sprint C.4 — implement SimilarityRanker for question bank vector search.
"""
