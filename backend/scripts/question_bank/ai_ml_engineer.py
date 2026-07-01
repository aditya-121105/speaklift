# backend/scripts/question_bank/ai_ml_engineer.py
"""
AI/ML Engineer question collection.

Expose: QUESTIONS (list[QuestionBank])
"""

from app.models.question_bank import QuestionBank
from app.shared.enums import DifficultyLevel, ExperienceLevel, QuestionCategory

from .common import create_question

QUESTIONS: list[QuestionBank] = [

    create_question(
        role="AI/ML Engineer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "What is the difference between supervised and unsupervised learning? "
            "Give a real-world example of each."
        ),
        skills=["Machine Learning", "AI Fundamentals"],
        technologies=["scikit-learn", "Python"],
        expected_concepts=[
            "Labelled Data",
            "Unlabelled Data",
            "Classification",
            "Clustering",
            "Regression",
        ],
        has_follow_up=True,
    ),

    create_question(
        role="AI/ML Engineer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Explain overfitting and underfitting. "
            "What techniques would you use to detect and address each?"
        ),
        skills=["Machine Learning", "Model Evaluation"],
        technologies=["scikit-learn", "Python"],
        expected_concepts=[
            "Bias-Variance Tradeoff",
            "Cross-Validation",
            "Regularisation",
            "Dropout",
            "Learning Curves",
        ],
        has_follow_up=True,
    ),

    create_question(
        role="AI/ML Engineer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.ROLE_SPECIFIC,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Walk me through how you would build and evaluate "
            "a binary classification model from scratch."
        ),
        skills=["Machine Learning", "Feature Engineering", "Model Evaluation"],
        technologies=["scikit-learn", "pandas", "NumPy", "Python"],
        expected_concepts=[
            "Data Preprocessing",
            "Train/Test Split",
            "Model Selection",
            "Precision and Recall",
            "ROC-AUC",
            "Confusion Matrix",
        ],
        has_follow_up=True,
    ),
]
