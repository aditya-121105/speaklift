# backend/scripts/question_bank/cloud_engineer.py
"""
Cloud Engineer question collection.

Expose: QUESTIONS (list[QuestionBank])
"""

from app.models.question_bank import QuestionBank
from app.shared.enums import DifficultyLevel, ExperienceLevel, QuestionCategory

from .common import create_question

QUESTIONS: list[QuestionBank] = [

    create_question(
        role="Cloud Engineer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "What is the difference between IaaS, PaaS, and SaaS? "
            "Give an example of each from a major cloud provider."
        ),
        skills=["Cloud Computing", "Infrastructure"],
        technologies=["AWS", "GCP", "Azure"],
        expected_concepts=[
            "Infrastructure as a Service",
            "Platform as a Service",
            "Software as a Service",
            "Shared Responsibility Model",
            "Managed Services",
        ],
        has_follow_up=True,
    ),

    create_question(
        role="Cloud Engineer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Explain the difference between vertical and horizontal scaling. "
            "When would you choose each strategy on AWS?"
        ),
        skills=["Cloud Computing", "System Design", "Infrastructure"],
        technologies=["AWS EC2", "AWS Auto Scaling", "Load Balancer"],
        expected_concepts=[
            "Vertical Scaling",
            "Horizontal Scaling",
            "Auto Scaling Groups",
            "Load Balancing",
            "Cost Implications",
        ],
        has_follow_up=True,
    ),

    create_question(
        role="Cloud Engineer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.ROLE_SPECIFIC,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "How would you architect a highly available web application on AWS "
            "that serves users across multiple regions?"
        ),
        skills=["Cloud Architecture", "High Availability", "Infrastructure"],
        technologies=["AWS", "Route 53", "CloudFront", "RDS", "ALB"],
        expected_concepts=[
            "Multi-Region Deployment",
            "DNS Failover",
            "CDN",
            "Read Replicas",
            "RTO and RPO",
        ],
        has_follow_up=True,
    ),
]
