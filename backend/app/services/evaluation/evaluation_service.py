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

    def evaluate_session(
        self,
        db: Session,
        session_id: int,
        questions: list[InterviewQuestion],
        answers: list[InterviewAnswer],
        interview_context: str | None = None
    ) -> InterviewEvaluation:
        
        answer_map = {a.interview_question_id: a for a in answers}
        requests = []
        for q in questions:
            ans = answer_map.get(q.id)
            if ans and ans.transcript:
                sub_ans = SubmittedAnswer(
                    transcript=ans.transcript, 
                    answer_source=ans.answer_source
                )
                
                # Centralized placeholder defaults for fields not present in execution schema
                sel_q = SelectedQuestion(
                    question_id=str(q.id),
                    question_text=q.question_text,
                    category=q.question_category,
                    difficulty=DifficultyLevel.MEDIUM,
                    expected_duration_seconds=60,
                    tags=[],
                    ordering=q.question_order,
                    objective_name="General Evaluation"
                )
                requests.append(EvaluationRequest(submitted_answer=sub_ans, selected_question=sel_q))

        if not requests:
            raise ValueError("No answers to evaluate.")
            
        enhanced_answers = [self.evaluate_answer(req, interview_context) for req in requests]
        
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
        
        for ea in enhanced_answers:
            # Deterministic metrics are 0.0 to 1.0 (assuming from engine)
            base_score = int(ea.deterministic_metrics.overall_score * 100)
            t_score += base_score
            o_score += base_score
            beh_score += base_score  # Fallback for behavioral if NLP doesn't separate it
            
            if ea.ai_interpretation:
                has_ai = True
                strengths.extend([s.model_dump() for s in ea.ai_interpretation.strengths])
                weaknesses.extend([w.model_dump() for w in ea.ai_interpretation.weaknesses])
                recommendations.extend([r.model_dump() for r in ea.ai_interpretation.suggestions])
                
                com_score += rating_map.get(ea.ai_interpretation.communication.clarity_rating.value, 50)
                conf_score += rating_map.get(ea.ai_interpretation.communication.confidence_rating.value, 50)
            else:
                com_score += 50
                conf_score += 50

        count = len(requests)
        
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
