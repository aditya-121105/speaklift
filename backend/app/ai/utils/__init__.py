# backend/app/ai/utils/__init__.py
"""
AI Utilities
============

Shared utility functions used across multiple AI sub-packages.

Design rules
------------
- Only PURE, STATELESS functions belong here.
- No imports of business domain objects.
- No imports from sub-packages that import from utils/ (no circular deps).
- Functions here must be generic — if a utility only makes sense inside
  one sub-package, it belongs there, not here.

Planned utilities
-----------------
Text utilities
    truncate_to_token_limit(text, max_tokens, tokenizer) -> str
        Truncate text to fit within a token budget. Used before
        sending prompts to providers with limited context windows.

    chunk_text(text, chunk_size, overlap) -> list[str]
        Split long documents into overlapping chunks for embedding.
        Used by document_processing/ and nlp/.

    clean_whitespace(text) -> str
        Normalise unicode whitespace, remove zero-width chars, etc.
        Shared between document_processing/cleaners/ and nlp/processors/.

Scoring utilities
    clamp(value, min_val, max_val) -> float
        Clamp a float to [min_val, max_val]. Used by all scorer outputs.

    normalise_score(raw, min_raw, max_raw) -> float
        Map a raw score to [0.0, 1.0]. Used across evaluation scorers.

Validation utilities
    validate_non_empty(text, field_name) -> None
        Raise AIValidationError if text is empty. Shared guard used by
        extractors, providers, and embedders.

Sprint C.2 — skeleton only.
Sprint C.3+ — add utilities as they become needed by implementations.
"""
