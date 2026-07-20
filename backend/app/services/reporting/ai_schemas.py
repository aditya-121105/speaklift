from pydantic import BaseModel
from typing import List
from app.services.reporting.schemas import (
    HiringRecommendation, 
    LearningRoadmap,
)

class AIExecutiveSummary(BaseModel):
    overall_performance: str
    confidence_level: str
    narrative: str

class AIHiringRecommendation(HiringRecommendation):
    pass

class AILearningRoadmap(LearningRoadmap):
    pass

class AICompetencyAssessment(BaseModel):
    competency_name: str
    score: int
    evidence: str
    strengths: List[str]
    weaknesses: List[str]
    missing_concepts: List[str]
    demonstrated_concepts: List[str]

class AIReportGenerationResult(BaseModel):
    executive_summary: AIExecutiveSummary
    competencies: List[AICompetencyAssessment]
    hiring_recommendation: AIHiringRecommendation
    learning_roadmap: AILearningRoadmap
