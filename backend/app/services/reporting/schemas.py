from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class HiringDecision(str, Enum):
    HIRE = "HIRE"
    HIRE_WITH_RESERVATIONS = "HIRE_WITH_RESERVATIONS"
    BORDERLINE = "BORDERLINE"
    NO_HIRE = "NO_HIRE"

class ExecutiveSummary(BaseModel):
    overall_performance: str = Field(..., description="High-level summary of candidate's performance")
    completion_status: str = Field(..., description="E.g., Completed, Incomplete")
    overall_score: int = Field(..., description="Aggregated score from 0 to 100")
    confidence_level: str = Field(..., description="E.g., High, Medium, Low")
    narrative: str = Field(..., description="Executive summary narrative for the recruiter")

class CompetencyAssessment(BaseModel):
    competency_name: str
    score: int
    evidence: str
    strengths: List[str]
    weaknesses: List[str]
    missing_concepts: List[str]
    demonstrated_concepts: List[str]

class CommunicationAssessment(BaseModel):
    grammar_score: int
    readability_score: int
    vocabulary_richness: int
    confidence_rating: str
    clarity_rating: str
    overall_quality: str

class QuestionReview(BaseModel):
    question_id: str
    planned_order: int
    execution_path: str
    question_text: str
    candidate_answer: str
    is_follow_up: bool
    evaluation_summary: str
    score: int
    evidence: str
    improvement_suggestions: List[str]

class HiringRecommendation(BaseModel):
    decision: HiringDecision
    confidence: str
    reasoning: str
    supporting_evidence: List[str]

class LearningObjective(BaseModel):
    topic: str
    description: str
    difficulty: str
    rationale: str

class LearningRoadmap(BaseModel):
    prioritized_skill_gaps: List[str]
    learning_sequence: List[LearningObjective]

class InterviewStatistics(BaseModel):
    total_questions_asked: int
    primary_questions: int
    follow_up_questions: int
    average_confidence: int
    average_semantic_similarity: int
    average_grammar: int
    average_readability: int
    interview_duration_seconds: int

class InterviewReport(BaseModel):
    session_id: int
    executive_summary: ExecutiveSummary
    competencies: List[CompetencyAssessment]
    communication: CommunicationAssessment
    question_reviews: List[QuestionReview]
    hiring_recommendation: HiringRecommendation
    learning_roadmap: LearningRoadmap
    statistics: InterviewStatistics
