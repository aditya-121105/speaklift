from sqlalchemy.orm import Session

from app.services.interview_execution.execution_service import InterviewExecutionService
from app.services.interview_planner.planner import InterviewPlanner
from app.services.question_selection.selector import QuestionSelector
from app.services.matching.engine import MatchingEngine
from app.services.interview_session_service import InterviewSessionService
from app.services.interview_context.builder import InterviewContextBuilder
from app.services.interview_execution.schemas.interview_execution_state import InterviewExecutionState

from datetime import datetime

from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.candidate_profile.schemas.technology import TechnologyProfile
from app.services.candidate_profile.schemas.identity import IdentityProfile, ContactInformation, SocialProfile
from app.services.candidate_profile.schemas.career import CareerProfile, CareerStage
from app.services.candidate_profile.schemas.education import EducationProfile
from app.services.candidate_profile.schemas.metadata import ProfileMetadata as CandidateMetadata

from app.services.job_profile.schemas.profile import JobProfile
from app.services.job_profile.schemas.requirements import RequirementsProfile
from app.services.job_profile.schemas.identity import JobIdentity
from app.services.job_profile.schemas.employment import EmploymentProfile
from app.services.job_profile.schemas.qualification import QualificationProfile, ExperienceRequirements, EducationRequirements
from app.services.job_profile.schemas.company import CompanyProfile
from app.services.job_profile.schemas.metadata import ProfileMetadata as JobMetadata

from app.repositories.resume_repository import ResumeRepository
from app.repositories.job_description_repository import JobDescriptionRepository


def _build_empty_candidate_profile() -> CandidateProfile:
    return CandidateProfile.model_construct(
        identity=IdentityProfile.model_construct(
            full_name=None, contact=ContactInformation.model_construct(), social=SocialProfile.model_construct()
        ),
        career=CareerProfile.model_construct(
            career_stage=CareerStage.ENTRY, current_role=None, most_recent_employer=None,
            total_months_experience=0, internship_months=0, positions=[]
        ),
        education=EducationProfile.model_construct(
            highest_qualification=None, latest_institution=None, is_currently_studying=False,
            degrees=[], certifications=[]
        ),
        technology=TechnologyProfile.model_construct(
            languages=[], frameworks=[], libraries=[], databases=[], cloud=[],
            devops=[], ai_ml=[], testing=[], operating_systems=[], tools=[]
        ),
        projects=[],
        certifications=[],
        metadata=CandidateMetadata.model_construct(
            pipeline_version="0.0.0", profile_version="0.0.0", generated_timestamp=datetime.utcnow(),
            average_confidence=0.0, processing_duration_ms=0
        )
    )

def _build_empty_job_profile() -> JobProfile:
    return JobProfile.model_construct(
        identity=JobIdentity.model_construct(job_title=None, raw_title=None, location=None, remote_type=None),
        requirements=RequirementsProfile.model_construct(
            required_skills=[], preferred_skills=[], optional_skills=[], unknown_skills=[], responsibilities=[]
        ),
        technology=TechnologyProfile.model_construct(
            languages=[], frameworks=[], libraries=[], databases=[], cloud=[],
            devops=[], ai_ml=[], testing=[], operating_systems=[], tools=[]
        ),
        qualification=QualificationProfile.model_construct(
            experience=ExperienceRequirements.model_construct(min_years=None, max_years=None),
            education=EducationRequirements.model_construct(minimum_degree=None, degrees=[])
        ),
        employment=EmploymentProfile.model_construct(employment_type=None, salary=None),
        company=CompanyProfile.model_construct(name=None, industry=None, size=None, culture_keywords=[]),
        metadata=JobMetadata.model_construct(
            profile_created_at=datetime.utcnow(), source_filename="empty", is_active=True
        )
    )

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
        candidate = _build_empty_candidate_profile()
        job = _build_empty_job_profile()
        
        if session.resume_id:
            resume = ResumeRepository.get_by_id_and_user(db, session.resume_id, user_id)
            if resume and resume.candidate_profile_data:
                candidate = CandidateProfile.model_validate(resume.candidate_profile_data)
                
        if session.job_description_id:
            jd = JobDescriptionRepository.get_by_id_and_user(db, session.job_description_id, user_id)
            if jd and jd.job_profile_data:
                job = JobProfile.model_validate(jd.job_profile_data)

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
        return self._execution_service.start_interview(db, session_id, user_id, selection)
