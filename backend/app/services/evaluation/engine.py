from app.services.evaluation.schemas.evaluation_request import EvaluationRequest
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
from app.services.evaluation.protocols import TextProcessorProtocol, VocabularyExtractorProtocol

class DeterministicEvaluationEngine:
    
    def __init__(
        self,
        text_processor: TextProcessorProtocol,
        vocabulary_extractor: VocabularyExtractorProtocol,
    ):
        self._text_processor = text_processor
        self._vocabulary_extractor = vocabulary_extractor

    def evaluate(self, request: EvaluationRequest) -> AnswerEvaluation:
        answer_text = request.submitted_answer.transcript.strip()
        question_text = request.selected_question.question_text.strip()
        
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
        
        if not question_text:
            completeness = min(1.0, len(answer_doc.tokens) / 50.0)
            return AnswerEvaluation(
                keyword_coverage=0.0,
                concept_coverage=0.0,
                completeness=completeness,
                vocabulary_statistics=vocab_stats,
                overall_score=0.0,
            )
            
        question_doc = self._text_processor.process(question_text)
        
        question_content = set(question_doc.content_words)
        answer_content = set(answer_doc.content_words)
        
        if question_content:
            keyword_coverage = len(question_content.intersection(answer_content)) / len(question_content)
        else:
            keyword_coverage = 0.0
            
        question_entities = set(question_doc.named_entities)
        answer_entities = set(answer_doc.named_entities)
        
        if question_entities:
            concept_coverage = len(question_entities.intersection(answer_entities)) / len(question_entities)
        else:
            concept_coverage = keyword_coverage
            
        completeness = min(1.0, len(answer_doc.tokens) / 50.0)
        
        overall_score = (keyword_coverage * 0.4) + (concept_coverage * 0.4) + (completeness * 0.2)
        
        return AnswerEvaluation(
            keyword_coverage=keyword_coverage,
            concept_coverage=concept_coverage,
            completeness=completeness,
            vocabulary_statistics=vocab_stats,
            overall_score=overall_score,
        )
