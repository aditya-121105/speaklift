from sqlalchemy.orm import Session
from app.models.interview_session import InterviewSession
from app.models.interview_question import InterviewQuestion
from app.models.interview_answer import InterviewAnswer
from app.models.answer_evaluation import AnswerEvaluation
from app.models.interview_evaluation import InterviewEvaluation

from app.services.reporting.schemas import (
    InterviewReport,
    ExecutiveSummary,
    CommunicationAssessment,
    QuestionReview,
    InterviewStatistics,
    CompetencyAssessment
)
from app.services.reporting.ai_schemas import AIReportGenerationResult
from app.services.reporting.prompt_builder import ReportPromptBuilder
from app.ai.llm.services.llm_service import LLMService

class InterviewReportService:
    def __init__(self, llm_service: LLMService):
        self._llm_service = llm_service

    def generate_report(self, db: Session, session_id: int) -> InterviewReport:
        # Fetch the session
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        # Fetch questions
        questions = db.query(InterviewQuestion).filter(InterviewQuestion.interview_session_id == session_id).order_by(InterviewQuestion.execution_path).all()
        question_ids = [q.id for q in questions]

        # Fetch answers
        answers = db.query(InterviewAnswer).filter(InterviewAnswer.interview_question_id.in_(question_ids)).all()
        answer_map = {a.interview_question_id: a for a in answers}
        answer_ids = [a.id for a in answers]

        # Fetch evaluations
        evaluations = db.query(AnswerEvaluation).filter(AnswerEvaluation.interview_answer_id.in_(answer_ids)).all()
        eval_map = {e.interview_answer_id: e for e in evaluations}
        
        # Fetch session level evaluation
        session_eval = db.query(InterviewEvaluation).filter(InterviewEvaluation.interview_session_id == session_id).first()

        # Build basic stats and aggregates
        total_answers = len(answers)
        primary_q = sum(1 for q in questions if q.question_type.value == "PRIMARY")
        follow_up_q = sum(1 for q in questions if q.question_type.value == "FOLLOW_UP")
        
        # Compute averages for stats and communication
        avg_conf = 0.0
        avg_sem = 0.0
        avg_gram = 0.0
        avg_read = 0.0
        duration = 0
        
        vocab_total = 0
        conf_count = 0
        sem_count = 0
        gram_count = 0
        read_count = 0
        
        questions_and_evals = []
        question_reviews = []

        for q in questions:
            ans = answer_map.get(q.id)
            if not ans:
                continue
                
            duration += (ans.answer_duration_seconds or 0)
            e = eval_map.get(ans.id)
            if not e:
                continue
                
            if e.confidence_score is not None:
                avg_conf += e.confidence_score
                conf_count += 1
            if e.semantic_similarity is not None:
                avg_sem += e.semantic_similarity
                sem_count += 1
            if e.grammar_score is not None:
                avg_gram += e.grammar_score
                gram_count += 1
            if e.readability_score is not None:
                avg_read += e.readability_score
                read_count += 1
                
            vocab_stat = e.vocabulary_statistics or {}
            vocab_total += vocab_stat.get("unique_words", 0)

            questions_and_evals.append({
                "planned_order": q.planned_order,
                "execution_path": q.execution_path,
                "question_text": q.question_text,
                "category": q.question_category.value if hasattr(q.question_category, 'value') else q.question_category,
                "answer_transcript": ans.transcript,
                "score": int(e.overall_score * 100),
                "strengths": e.strengths or [],
                "weaknesses": e.weaknesses or []
            })
            
            question_reviews.append(
                QuestionReview(
                    question_id=str(q.id),
                    planned_order=q.planned_order,
                    execution_path=q.execution_path,
                    question_text=q.question_text,
                    candidate_answer=ans.transcript,
                    is_follow_up=(q.question_type.value == "FOLLOW_UP"),
                    evaluation_summary=e.communication_feedback or "No feedback available.",
                    score=int(e.overall_score * 100),
                    evidence="Determined from lexical and semantic analysis.",
                    improvement_suggestions=e.recommendations or []
                )
            )

        avg_conf = int(avg_conf / conf_count * 100) if conf_count else 0
        avg_sem = int(avg_sem / sem_count * 100) if sem_count else 0
        avg_gram = int(avg_gram / gram_count * 100) if gram_count else 0
        avg_read = int(avg_read / read_count * 100) if read_count else 0

        statistics = InterviewStatistics(
            total_questions_asked=total_answers,
            primary_questions=primary_q,
            follow_up_questions=follow_up_q,
            average_confidence=avg_conf,
            average_semantic_similarity=avg_sem,
            average_grammar=avg_gram,
            average_readability=avg_read,
            interview_duration_seconds=duration
        )

        overall_quality = "Fair"
        if avg_gram > 80 and avg_read > 80:
            overall_quality = "Excellent"
        elif avg_gram > 60:
            overall_quality = "Good"
            
        overall_score = session_eval.overall_score if session_eval else 0

        communication = CommunicationAssessment(
            grammar_score=avg_gram,
            readability_score=avg_read,
            vocabulary_richness=vocab_total // total_answers if total_answers else 0,
            confidence_rating="High" if avg_conf > 80 else ("Low" if avg_conf < 50 else "Medium"),
            clarity_rating="High" if avg_sem > 80 else ("Low" if avg_sem < 50 else "Medium"),
            overall_quality=overall_quality
        )

        context_data = {
            "statistics": statistics.model_dump(),
            "communication": communication.model_dump(),
            "overall_session_score": overall_score
        }

        # Build prompt
        prompt = ReportPromptBuilder.build_report_prompt(
            session_id=session_id,
            context_data=context_data,
            questions_and_evals=questions_and_evals
        )

        # Generate from AI
        ai_result: AIReportGenerationResult = self._llm_service.generate_json(
            prompt=prompt,
            response_schema=AIReportGenerationResult
        )

        exec_summary = ExecutiveSummary(
            overall_performance=ai_result.executive_summary.overall_performance,
            completion_status=session.status.value,
            overall_score=overall_score,
            confidence_level=ai_result.executive_summary.confidence_level,
            narrative=ai_result.executive_summary.narrative
        )

        return InterviewReport(
            session_id=session_id,
            executive_summary=exec_summary,
            competencies=[CompetencyAssessment(**c.model_dump()) for c in ai_result.competencies],
            communication=communication,
            question_reviews=question_reviews,
            hiring_recommendation=ai_result.hiring_recommendation.model_dump(),
            learning_roadmap=ai_result.learning_roadmap.model_dump(),
            statistics=statistics
        )
