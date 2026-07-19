"""
==============================================================================
Module:
    Confidence Feature Extractor

Milestone:
    M2.1 – Evaluation Engine Completion

Purpose:
    Detects verbal confidence markers in a candidate's answer using a
    deterministic, lexicon-based approach.

Strategy
--------
Two categories of confidence detractors are measured:

1. Filler words
   Single tokens commonly used as verbal pauses:
   "um", "uh", "er", "hmm", "ah", "like", "you know", "right", "okay"

2. Hedging phrases
   Multi-word phrases signalling uncertainty:
   "I think", "I believe", "maybe", "kind of", "sort of",
   "I'm not sure", "I guess", "perhaps", "it could be"

A confidence_score of 1.0 means the answer contains zero confidence
detractors. Each unique filler or hedging phrase type detected reduces
the score by a configurable penalty (default: 0.1 per type), floored at 0.

Responsibilities:
    ✔ Detect and count filler words
    ✔ Detect and count hedging phrases
    ✔ Compute a normalised confidence score
    ✔ List distinct detected indicators

Does NOT:
    ✘ Use AI models
    ✘ Access the database
    ✘ Evaluate the factual correctness of the answer
==============================================================================
"""

import re

from app.services.evaluation.schemas.confidence_evaluation import ConfidenceEvaluation

# Single-token filler words (matched case-insensitively)
_FILLER_TOKENS: frozenset[str] = frozenset(
    {
        "um",
        "uh",
        "er",
        "hmm",
        "ah",
        "erm",
        "like",
        "basically",
        "literally",
        "actually",
        "you know",      # handled as phrase below; kept here for completeness
        "right",
        "okay",
        "so",
        "well",
        "anyway",
    }
)

# Multi-word hedging phrases (matched as substrings, case-insensitive)
_HEDGING_PHRASES: list[str] = [
    "i think",
    "i believe",
    "i guess",
    "i'm not sure",
    "i am not sure",
    "i'm not certain",
    "i am not certain",
    "maybe",
    "perhaps",
    "possibly",
    "kind of",
    "sort of",
    "might be",
    "could be",
    "probably",
    "more or less",
    "in a way",
    "to some extent",
    "you know",
    "i suppose",
    "not really sure",
]

# Penalty per distinct indicator type found
_PENALTY_PER_TYPE: float = 0.1


class ConfidenceFeatureExtractor:
    """
    Extract deterministic confidence indicators from a raw text string.
    """

    def extract(self, text: str) -> ConfidenceEvaluation:
        if not text.strip():
            return ConfidenceEvaluation(
                filler_word_count=0,
                hedging_phrase_count=0,
                filler_word_ratio=0.0,
                detected_fillers=[],
                confidence_score=1.0,
                summary="Empty answer – no confidence analysis performed.",
            )

        normalized = text.lower()

        # --- Filler token matching (whole-word, single token) ---
        words = re.findall(r"\b\w+\b", normalized)
        total_words = max(len(words), 1)

        filler_hit_tokens: list[str] = []
        for token_filler in sorted(_FILLER_TOKENS - {"you know"}):
            count = words.count(token_filler)
            filler_hit_tokens.extend([token_filler] * count)

        filler_word_count = len(filler_hit_tokens)

        # --- Hedging phrase matching ---
        hedging_hit_phrases: list[str] = []
        for phrase in _HEDGING_PHRASES:
            # Use word-boundary-aware regex
            pattern = r"\b" + re.escape(phrase) + r"\b"
            matches = re.findall(pattern, normalized)
            hedging_hit_phrases.extend(matches)

        hedging_phrase_count = len(hedging_hit_phrases)

        # --- Distinct indicators (for reporting) ---
        distinct_fillers = sorted(set(filler_hit_tokens))
        distinct_hedges = sorted(set(hedging_hit_phrases))
        detected_all = distinct_fillers + distinct_hedges

        # --- Score ---
        distinct_types = len(set(filler_hit_tokens) | set(hedging_hit_phrases))
        confidence_score = max(0.0, 1.0 - distinct_types * _PENALTY_PER_TYPE)

        filler_ratio = filler_word_count / total_words

        # Summary
        total_indicators = filler_word_count + hedging_phrase_count
        if total_indicators == 0:
            summary = "Answer shows confident language – no filler words or hedging detected."
        elif total_indicators <= 3:
            summary = (
                f"Mild confidence detractors found ({total_indicators} instance(s)): "
                + ", ".join(detected_all[:5])
                + "."
            )
        else:
            summary = (
                f"Frequent confidence detractors ({total_indicators} instance(s)); "
                "response may appear uncertain or hesitant."
            )

        return ConfidenceEvaluation(
            filler_word_count=filler_word_count,
            hedging_phrase_count=hedging_phrase_count,
            filler_word_ratio=round(filler_ratio, 4),
            detected_fillers=detected_all,
            confidence_score=round(confidence_score, 4),
            summary=summary,
        )
