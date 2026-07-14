from sqlalchemy.orm import Session
from app.models.user import User

from app.services.interview_execution.execution_service import InterviewExecutionService
from app.services.interview_planner.planner import InterviewPlanner
from app.services.question_selection.selector import QuestionSelector
from app.services.matching.engine import MatchingEngine
from app.services.interview_session_service import InterviewSessionService
from app.services.interview_context.builder import InterviewContextBuilder
from app.services.interview_execution.schemas.interview_execution_state import InterviewExecutionState

from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.job_profile.schemas.profile import JobProfile
from app.repositories.resume_repository import ResumeRepository
from app.repositories.job_description_repository import JobDescriptionRepository


class InterviewWorkflowService:
    """
    Facade orchestrator for the Interview Engine.
    Coordinates Matcher, Planner, Selector, and Execution.
    """

    def __init__(
        self,
        execution_service: InterviewExecutionService,
        question_selector: QuestionSelector,
        planner: InterviewPlanner,
        matching_engine: MatchingEngine,
    ):
        self._execution_service = execution_service
        self._question_selector = question_selector
        self._planner = planner
        self._matching_engine = matching_engine

    def start_workflow(
        self, db: Session, session_id: int, user_id: int
    ) -> InterviewExecutionState:
        # 1. Fetch the existing session
        session = InterviewSessionService.get_interview_session(db, session_id, user_id)

        # 2. Build or Fetch Context Profiles
        candidate = CandidateProfile.model_construct(projects=[], certifications=[])
        job = JobProfile.model_construct()
        
        if session.resume_id:
            resume = ResumeRepository.get_by_id_and_user(db, session.resume_id, user_id)
            if resume and resume.candidate_profile_data:
                candidate = CandidateProfile.model_validate(resume.candidate_profile_data)
                
        if session.job_description:
            try:
                jd_id = int(session.job_description)
                jd = JobDescriptionRepository.get_by_id_and_user(db, jd_id, user_id)
                if jd and jd.job_profile_data:
                    job = JobProfile.model_validate(jd.job_profile_data)
            except ValueError:
                # If it's raw text and not an ID, we fall back to an empty construct for now
                pass

        # 3. Invoke Matching Engine
        match_result = self._matching_engine.match(candidate, job)

        # 4. Invoke Interview Planner
        context = InterviewContextBuilder.build(
            candidate_profile=candidate,
            job_profile=job,
            match_result=match_result,
            interview_session=session,
        )
        plan = self._planner.build(context)

        # 5. Invoke Question Selector
        selection = self._question_selector.select_questions(db, plan)

        # 6. Start Execution
        return self._execution_service.start_interview(db, session_id, selection)
