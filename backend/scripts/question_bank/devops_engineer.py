# backend/scripts/question_bank/devops_engineer.py
"""
DevOps Engineer question collection.

Expose: QUESTIONS (list[QuestionBank])
"""

from app.models.question_bank import QuestionBank
from app.shared.enums import DifficultyLevel, ExperienceLevel, QuestionCategory

from .common import create_question

QUESTIONS: list[QuestionBank] = [

    create_question(
        role="DevOps Engineer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "What is the difference between continuous integration, "
            "continuous delivery, and continuous deployment?"
        ),
        skills=["DevOps", "CI/CD", "Software Delivery"],
        technologies=["GitHub Actions", "Jenkins", "GitLab CI"],
        expected_concepts=[
            "Automated Testing",
            "Build Pipeline",
            "Deployment Automation",
            "Manual Approval Gates",
            "Trunk-Based Development",
        ],
        has_follow_up=True,
    ),

    create_question(
        role="DevOps Engineer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Explain how Docker containers differ from virtual machines. "
            "What problem does containerisation solve for a DevOps team?"
        ),
        skills=["DevOps", "Containerisation", "Infrastructure"],
        technologies=["Docker", "Docker Compose", "Kubernetes"],
        expected_concepts=[
            "OS-level Virtualisation",
            "Image Layers",
            "Portability",
            "Environment Consistency",
            "Resource Overhead",
        ],
        has_follow_up=True,
    ),

    create_question(
        role="DevOps Engineer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.ROLE_SPECIFIC,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "A production deployment fails and the application goes down. "
            "Walk me through your incident response process."
        ),
        skills=["Incident Management", "DevOps", "Reliability Engineering"],
        technologies=["CloudWatch", "PagerDuty", "Grafana", "kubectl"],
        expected_concepts=[
            "Rollback Strategy",
            "Observability",
            "Alerting",
            "Postmortem",
            "MTTR",
            "Blameless Culture",
        ],
        has_follow_up=True,
    ),
]
