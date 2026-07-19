"""
==============================================================================
Module:
    Deterministic Evaluation Engine

Milestone:
    M2.1 – Evaluation Engine Completion  (updated from M1 baseline)

Responsibilities:
    ✔ Orchestrate all deterministic feature extractors
    ✔ Keyword coverage   (content-word intersection)
    ✔ Concept coverage   (named-entity intersection)
    ✔ Completeness       (token-length heuristic)
    ✔ Vocabulary stats   (VocabularyFeatureExtractor)
    ✔ Grammar            (GrammarFeatureExtractor)
    ✔ Readability        (ReadabilityFeatureExtractor)
    ✔ Confidence         (ConfidenceFeatureExtractor)
    ✔ Semantic similarity (SemanticSimilarityFeatureExtractor)

Architecture
------------
The engine is entirely stateless and deterministic.
Every extractor is injected via constructor for full testability.
All new extractors are optional via keyword flags so callers can
disable expensive operations (e.g., embedding model) when not needed.

Does NOT:
    ✘ Call AI / LLM APIs
    ✘ Access the database
    ✘ Modify the EvaluationRequest
==============================================================================
"""

from app.services.evaluation.schemas.evaluation_request import EvaluationRequest
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
from app.services.evaluation.protocols import TextProcessorProtocol, VocabularyExtractorProtocol
from app.services.evaluation.feature_extractors.text.grammar_feature_extractor import (
    GrammarFeatureExtractor,
)
from app.services.evaluation.feature_extractors.text.readability_feature_extractor import (
    ReadabilityFeatureExtractor,
)
from app.services.evaluation.feature_extractors.text.confidence_feature_extractor import (
    ConfidenceFeatureExtractor,
)
from app.services.evaluation.feature_extractors.text.semantic_similarity_feature_extractor import (
    SemanticSimilarityFeatureExtractor,
)


class DeterministicEvaluationEngine:
    """
    Orchestrates all deterministic feature extractors and returns a fully
    populated AnswerEvaluation.

    Parameters
    ----------
    text_processor         : Converts raw text to TextDocument (spaCy).
    vocabulary_extractor   : Vocabulary richness / lexical density.
    grammar_extractor      : Grammar quality via dep-parse heuristics.
    readability_extractor  : Flesch Reading Ease & Flesch-Kincaid Grade.
    confidence_extractor   : Filler-word / hedging confidence indicators.
    semantic_extractor     : Embedding cosine similarity.
    """

    # Length (in tokens) at which completeness reaches 1.0
    COMPLETENESS_TARGET_TOKENS: int = 50

    def __init__(
        self,
        text_processor: TextProcessorProtocol,
        vocabulary_extractor: VocabularyExtractorProtocol,
        grammar_extractor: GrammarFeatureExtractor | None = None,
        readability_extractor: ReadabilityFeatureExtractor | None = None,
        confidence_extractor: ConfidenceFeatureExtractor | None = None,
        semantic_extractor: SemanticSimilarityFeatureExtractor | None = None,
    ) -> None:
        self._text_processor = text_processor
        self._vocabulary_extractor = vocabulary_extractor
        self._grammar_extractor = grammar_extractor
        self._readability_extractor = readability_extractor
        self._confidence_extractor = confidence_extractor
        self._semantic_extractor = semantic_extractor

    def evaluate(self, request: EvaluationRequest) -> AnswerEvaluation:
        answer_text = request.submitted_answer.transcript.strip()
        question_text = request.selected_question.question_text.strip()

        # --- Empty answer fast-path ---
        if not answer_text:
            return AnswerEvaluation(
                keyword_coverage=0.0,
                concept_coverage=0.0,
                completeness=0.0,
                vocabulary_statistics={},
                overall_score=0.0,
            )

        answer_doc = self._text_processor.process(answer_text)
        vocab_stats = self._vocabulary_extractor.extract([answer_doc])

        # --- Empty question fast-path ---
        if not question_text:
            completeness = min(
                1.0,
                len(answer_doc.tokens) / self.COMPLETENESS_TARGET_TOKENS,
            )
            return AnswerEvaluation(
                keyword_coverage=0.0,
                concept_coverage=0.0,
                completeness=completeness,
                vocabulary_statistics=vocab_stats,
                overall_score=0.0,
            )

        question_doc = self._text_processor.process(question_text)

        # --- Keyword coverage (content-word intersection) ---
        question_content = set(question_doc.content_words)
        answer_content = set(answer_doc.content_words)
        keyword_coverage = (
            len(question_content & answer_content) / len(question_content)
            if question_content
            else 0.0
        )

        # --- Concept coverage (named-entity intersection) ---
        question_entities = set(question_doc.named_entities)
        answer_entities = set(answer_doc.named_entities)
        concept_coverage = (
            len(question_entities & answer_entities) / len(question_entities)
            if question_entities
            else keyword_coverage  # fallback when question has no entities
        )

        # --- Completeness ---
        completeness = min(
            1.0,
            len(answer_doc.tokens) / self.COMPLETENESS_TARGET_TOKENS,
        )

        # --- Core weighted score ---
        overall_score = (
            keyword_coverage * 0.4
            + concept_coverage * 0.4
            + completeness * 0.2
        )

        # --- Extended extractors (all optional) ---
        grammar = (
            self._grammar_extractor.extract(answer_text)
            if self._grammar_extractor
            else None
        )
        readability = (
            self._readability_extractor.extract(answer_text)
            if self._readability_extractor
            else None
        )
        confidence = (
            self._confidence_extractor.extract(answer_text)
            if self._confidence_extractor
            else None
        )
        semantic_similarity = (
            self._semantic_extractor.extract(question_text, answer_text)
            if self._semantic_extractor
            else None
        )

        return AnswerEvaluation(
            keyword_coverage=keyword_coverage,
            concept_coverage=concept_coverage,
            completeness=completeness,
            vocabulary_statistics=vocab_stats,
            overall_score=overall_score,
            grammar=grammar,
            readability=readability,
            confidence=confidence,
            semantic_similarity=semantic_similarity,
        )
