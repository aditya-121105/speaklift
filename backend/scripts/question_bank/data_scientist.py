# backend/scripts/question_bank/data_scientist.py
"""
Data Scientist question collection.

Expose: QUESTIONS (list[QuestionBank])
"""

from app.models.question_bank import QuestionBank
from app.shared.enums import DifficultyLevel, ExperienceLevel, QuestionCategory

from .common import create_question

QUESTIONS: list[QuestionBank] = [

    create_question(
        role="Data Scientist",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "How do you handle missing values in a dataset? "
            "What are the trade-offs of different strategies?"
        ),
        skills=["Data Analysis", "Data Cleaning", "Statistics"],
        technologies=["pandas", "NumPy", "Python"],
        expected_concepts=[
            "Imputation",
            "Mean/Median/Mode",
            "Dropping Rows",
            "Forward Fill",
            "Impact on Model Bias",
        ],
        has_follow_up=True,
    ),

    create_question(
        role="Data Scientist",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Explain the difference between correlation and causation. "
            "How does this distinction affect data-driven decisions?"
        ),
        skills=["Statistics", "Data Analysis", "Critical Thinking"],
        technologies=["Python", "pandas", "scipy"],
        expected_concepts=[
            "Pearson Correlation",
            "Confounding Variables",
            "A/B Testing",
            "Experimental Design",
            "Simpson's Paradox",
        ],
        has_follow_up=True,
    ),

    create_question(
        role="Data Scientist",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.ROLE_SPECIFIC,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Describe your end-to-end approach to an exploratory data analysis (EDA). "
            "What do you look for and why?"
        ),
        skills=["Data Analysis", "Data Visualisation", "Statistics"],
        technologies=["pandas", "matplotlib", "seaborn", "Python"],
        expected_concepts=[
            "Descriptive Statistics",
            "Distribution Analysis",
            "Outlier Detection",
            "Correlation Heatmaps",
            "Feature Relationships",
        ],
        has_follow_up=True,
    ),
]
