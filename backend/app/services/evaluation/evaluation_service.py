import logging
from app.services.evaluation.engine import DeterministicEvaluationEngine
from app.ai.llm.services.llm_service import LLMService
from app.services.evaluation.schemas.evaluation_request import EvaluationRequest
from app.services.evaluation.schemas.ai_evaluation import EnhancedAnswerEvaluation, AIEvaluationResult
from app.ai.llm.prompts.answer_evaluation_prompt import AnswerEvaluationPromptBuilder
from sqlalchemy.orm import Session
from app.models.interview_evaluation import InterviewEvaluation
from app.repositories.interview_evaluation_repository import InterviewEvaluationRepository
from app.shared.enums import EvaluationSource, DifficultyLevel
from app.models.interview_question import InterviewQuestion
from app.models.interview_answer import InterviewAnswer
from app.services.interview_execution.schemas.submitted_answer import SubmittedAnswer
from app.services.question_selection.schemas.question_selection import SelectedQuestion
from app.models.answer_evaluation import AnswerEvaluation
from app.repositories.answer_evaluation_repository import AnswerEvaluationRepository

logger = logging.getLogger(__name__)

class InterviewEvaluationService:
    """
    Business orchestrator combining deterministic NLP evaluation with AI qualitative evaluation.
    """
    def __init__(
        self,
        deterministic_engine: DeterministicEvaluationEngine,
        llm_service: LLMService,
    ):
        self._deterministic_engine = deterministic_engine
        self._llm_service = llm_service

    def evaluate_answer(
        self,
        request: EvaluationRequest,
        interview_context: str | None = None
    ) -> EnhancedAnswerEvaluation:
        # 1. Execute deterministic evaluation first.
        metrics = self._deterministic_engine.evaluate(request)
        
        # 2. Build the AI evaluation prompt.
        prompt = AnswerEvaluationPromptBuilder.build(
            question_text=request.selected_question.question_text,
            answer_text=request.submitted_answer.transcript,
            metrics=metrics,
            interview_context=interview_context
        )
        
        ai_result = None
        
        # 3. Invoke LLMService.generate_json().
        try:
            ai_result = self._llm_service.generate_json(prompt, AIEvaluationResult)
        except Exception as e:
            # Error Handling: Gracefully degrade.
            # If the LLM evaluation fails, preserve deterministic evaluation.
            logger.warning(f"AI evaluation failed for answer. Degrading to deterministic only. Error: {e}")
            
        # 4 & 5. Merge deterministic and AI results, returning EnhancedAnswerEvaluation.
        return EnhancedAnswerEvaluation(
            deterministic_metrics=metrics,
            ai_interpretation=ai_result
        )

    def persist_answer_evaluation(
        self,
        db: Session,
        answer_id: int,
        enhanced_eval: EnhancedAnswerEvaluation
    ) -> AnswerEvaluation:
        """
        Persists a completed answer evaluation to the database.
        """
        metrics = enhanced_eval.deterministic_metrics
        ai = enhanced_eval.ai_interpretation

        eval_record = AnswerEvaluation(
            interview_answer_id=answer_id,
            overall_score=metrics.overall_score,
            keyword_coverage=metrics.keyword_coverage,
            concept_coverage=metrics.concept_coverage,
            completeness=metrics.completeness,
            vocabulary_statistics=metrics.vocabulary_statistics,
        )

        if metrics.grammar:
            eval_record.grammar_score = metrics.grammar.grammar_quality_score
            eval_record.grammar_details = metrics.grammar.model_dump()
        if metrics.readability:
            eval_record.readability_score = metrics.readability.flesch_reading_ease
            eval_record.readability_details = metrics.readability.model_dump()
        if metrics.confidence:
            eval_record.confidence_score = metrics.confidence.confidence_score
            eval_record.confidence_details = metrics.confidence.model_dump()
        if metrics.semantic_similarity:
            eval_record.semantic_similarity = metrics.semantic_similarity.cosine_similarity
            eval_record.semantic_details = metrics.semantic_similarity.model_dump()

        if ai:
            eval_record.strengths = [s.model_dump() for s in ai.strengths]
            eval_record.weaknesses = [w.model_dump() for w in ai.weaknesses]
            eval_record.recommendations = [r.model_dump() for r in ai.suggestions]
            eval_record.communication_clarity = ai.communication.clarity_rating.value
            eval_record.communication_confidence = ai.communication.confidence_rating.value
            eval_record.communication_tone = ai.communication.tone
            eval_record.communication_feedback = ai.communication.feedback

        return AnswerEvaluationRepository.create(db, eval_record)

    def evaluate_session(
        self,
        db: Session,
        session_id: int,
        questions: list[InterviewQuestion],
        answers: list[InterviewAnswer],
        interview_context: str | None = None
    ) -> InterviewEvaluation:
        
        if not answers:
            raise ValueError("No answers to evaluate.")
            
        answer_ids = [a.id for a in answers]
        persisted_evals = db.query(AnswerEvaluation).filter(AnswerEvaluation.interview_answer_id.in_(answer_ids)).all()
        
        if not persisted_evals:
            raise ValueError("No persisted answer evaluations found for aggregation.")

        t_score = 0
        com_score = 0
        beh_score = 0
        conf_score = 0
        o_score = 0
        strengths = []
        weaknesses = []
        recommendations = []
        has_ai = False
        
        rating_map = {"EXCELLENT": 100, "GOOD": 75, "FAIR": 50, "NEEDS_IMPROVEMENT": 25}
        
        for pe in persisted_evals:
            base_score = int(pe.overall_score * 100)
            t_score += base_score
            o_score += base_score
            beh_score += base_score  
            
            if pe.communication_clarity and pe.communication_confidence:
                has_ai = True
                com_score += rating_map.get(pe.communication_clarity, 50)
                conf_score += rating_map.get(pe.communication_confidence, 50)
            else:
                com_score += 50
                conf_score += 50

            if pe.strengths:
                strengths.extend(pe.strengths)
            if pe.weaknesses:
                weaknesses.extend(pe.weaknesses)
            if pe.recommendations:
                recommendations.extend(pe.recommendations)

        count = len(persisted_evals)
        
        evaluation = InterviewEvaluation(
            interview_session_id=session_id,
            technical_score=t_score // count,
            communication_score=com_score // count,
            behavioral_score=beh_score // count,
            confidence_score=conf_score // count,
            overall_score=o_score // count,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            evaluation_source=EvaluationSource.HYBRID if has_ai else EvaluationSource.RULE_BASED
        )
        
        return InterviewEvaluationRepository.create(db, evaluation)
