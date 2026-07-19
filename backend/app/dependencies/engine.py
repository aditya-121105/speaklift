from app.services.interview_execution.execution_service import InterviewExecutionService
from app.services.question_selection.selector import QuestionSelector
from app.services.interview_planner.planner import InterviewPlanner
from app.services.matching.engine import MatchingEngine
from app.services.matching.matchers.skill_matcher import SkillMatcher
from app.services.matching.matchers.experience_matcher import ExperienceMatcher
from app.services.matching.matchers.education_matcher import EducationMatcher
from app.services.matching.builder import MatchResultBuilder
from app.services.interview_workflow_service import InterviewWorkflowService
from app.services.evaluation.evaluation_service import InterviewEvaluationService
from app.services.evaluation.engine import DeterministicEvaluationEngine
from app.services.evaluation.feature_extractors.text.text_processor import TextProcessor
from app.services.evaluation.feature_extractors.text.vocabulary_feature_extractor import VocabularyFeatureExtractor

from app.repositories.interview_session_repository import InterviewSessionRepository
from app.repositories.interview_question_repository import InterviewQuestionRepository
from app.repositories.interview_answer_repository import InterviewAnswerRepository
from app.repositories.question_bank_repository import QuestionBankRepository

from app.ai.llm.factory import get_llm_service
def get_matching_engine() -> MatchingEngine:
    return MatchingEngine(
        skill_matcher=SkillMatcher(),
        experience_matcher=ExperienceMatcher(),
        education_matcher=EducationMatcher(),
        result_builder=MatchResultBuilder()
    )

def get_planner() -> InterviewPlanner:
    return InterviewPlanner()

def get_question_selector() -> QuestionSelector:
    return QuestionSelector(repository=QuestionBankRepository())

def get_evaluation_service() -> InterviewEvaluationService:
    # Build Deterministic Engine
    text_processor = TextProcessor()
    vocabulary_extractor = VocabularyFeatureExtractor()
    
    deterministic_engine = DeterministicEvaluationEngine(
        text_processor=text_processor,
        vocabulary_extractor=vocabulary_extractor
    )
    
    # In a full DI setup, LLMService config would be parsed from settings. 
    # Using defaults for orchestration freeze sprint.
    llm_service = get_llm_service()
    
    return InterviewEvaluationService(
        deterministic_engine=deterministic_engine,
        llm_service=llm_service
    )

def get_execution_service() -> InterviewExecutionService:
    return InterviewExecutionService(
        session_repo=InterviewSessionRepository(),
        question_repo=InterviewQuestionRepository(),
        answer_repo=InterviewAnswerRepository(),
        evaluation_service=get_evaluation_service()
    )

def get_interview_workflow_service() -> InterviewWorkflowService:
    return InterviewWorkflowService(
        execution_service=get_execution_service(),
        question_selector=get_question_selector(),
        planner=get_planner(),
        matching_engine=get_matching_engine()
    )
