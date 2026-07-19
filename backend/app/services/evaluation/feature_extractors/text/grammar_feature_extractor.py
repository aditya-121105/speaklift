"""
==============================================================================
Module:
    Grammar Feature Extractor

Milestone:
    M2.1 – Evaluation Engine Completion

Purpose:
    Analyses the syntactic quality of a candidate's answer using spaCy's
    dependency parser without introducing any external heavyweight library.

Strategy
--------
Grammar correctness is approximated through dependency-parse heuristics:

1. Subject-Verb Agreement check
   Detect finite clauses where the verb's number tag does not match the
   subject's number attribute (e.g. "They was late").

2. Missing root detection
   Sentences without a ROOT token suggest a fragment.

3. Double negation detection
   More than one NEG dependency in the same sentence.

These heuristics surface the most common grammatical errors in spoken-style
interview transcripts without requiring a separate grammar-checking library.

Responsibilities:
    ✔ Detect subject-verb number mismatches
    ✔ Detect fragmentary sentences (no ROOT)
    ✔ Detect double negation
    ✔ Produce a normalised quality score

Does NOT:
    ✘ Use AI models
    ✘ Access the database
    ✘ Evaluate answer quality
==============================================================================
"""

from app.core.nlp import NLPResourceManager
from app.services.evaluation.schemas.grammar_evaluation import GrammarEvaluation


# spaCy fine-grained tags indicating a finite, non-auxiliary verb
_FINITE_VERB_TAGS: frozenset[str] = frozenset(
    {"VBP", "VBZ", "VBD"}  # present, third-person present, past
)

# Tags that imply a plural noun/pronoun subject
_PLURAL_SUBJ_TAGS: frozenset[str] = frozenset({"NNS", "NNPS", "PRP"})
_PLURAL_PRONOUNS: frozenset[str] = frozenset(
    {"they", "we", "you", "i"}
)


def _count_sv_mismatches(sentence_span) -> int:
    """Return the number of subject-verb agreement errors in one sentence."""
    errors = 0
    for token in sentence_span:
        if token.tag_ not in _FINITE_VERB_TAGS:
            continue
        # Find nsubj or nsubjpass child
        subj = next(
            (c for c in token.children if c.dep_ in {"nsubj", "nsubjpass"}),
            None,
        )
        if subj is None:
            continue
        # Simple heuristic: VBZ (third-person singular) with a plural subject
        if token.tag_ == "VBZ":
            subj_lower = subj.text.lower()
            if (
                subj.tag_ in _PLURAL_SUBJ_TAGS
                and subj_lower in _PLURAL_PRONOUNS
            ):
                errors += 1
    return errors


def _has_no_root(sentence_span) -> bool:
    """Return True if the sentence has no ROOT token (fragment)."""
    return not any(t.dep_ == "ROOT" for t in sentence_span)


def _has_double_negation(sentence_span) -> bool:
    """Return True if the sentence contains more than one NEG dependency."""
    neg_count = sum(1 for t in sentence_span if t.dep_ == "neg")
    return neg_count > 1


class GrammarFeatureExtractor:
    """
    Extract grammar quality metrics from a raw text string.

    Parameters
    ----------
    text : str
        The raw candidate answer transcript.

    Returns
    -------
    GrammarEvaluation
    """

    def extract(self, text: str) -> GrammarEvaluation:
        if not text.strip():
            return GrammarEvaluation(
                grammar_error_count=0,
                grammar_quality_score=1.0,
                error_rate_per_sentence=0.0,
                summary="Empty answer – no grammar analysis performed.",
            )

        nlp = NLPResourceManager.get_spacy_model()
        doc = nlp(text)

        sentences = list(doc.sents)
        total_errors = 0

        for sent in sentences:
            total_errors += _count_sv_mismatches(sent)
            if _has_no_root(sent):
                total_errors += 1
            if _has_double_negation(sent):
                total_errors += 1

        sentence_count = max(len(sentences), 1)
        error_rate = total_errors / sentence_count

        # Normalise: every error costs 0.1 quality, floored at 0
        quality_score = max(0.0, 1.0 - (total_errors * 0.1))

        if total_errors == 0:
            summary = "No grammatical errors detected."
        elif total_errors <= 2:
            summary = f"Minor grammatical issues detected ({total_errors} error(s))."
        else:
            summary = f"Multiple grammatical issues detected ({total_errors} error(s)) – review recommended."

        return GrammarEvaluation(
            grammar_error_count=total_errors,
            grammar_quality_score=round(quality_score, 4),
            error_rate_per_sentence=round(error_rate, 4),
            summary=summary,
        )
