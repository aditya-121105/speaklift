# backend/scripts/question_bank/python_developer.py
"""
Python Developer question collection.

Expose: QUESTIONS (list[QuestionBank])
"""

from app.models.question_bank import QuestionBank
from app.shared.enums import DifficultyLevel, ExperienceLevel, QuestionCategory

from .common import create_question

QUESTIONS: list[QuestionBank] = [

    create_question(
        role="Python Developer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.EASY,
        question_text=(
            "What is the difference between a list and a tuple in Python? "
            "When would you choose one over the other?"
        ),
        skills=["Python", "Data Structures"],
        technologies=["Python"],
        expected_concepts=[
            "Mutability",
            "Immutability",
            "Memory Efficiency",
            "Hashability",
            "Use Cases",
        ],
        has_follow_up=True,
    ),

    create_question(
        role="Python Developer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.TECHNICAL,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "Explain Python's GIL (Global Interpreter Lock). "
            "How does it affect multi-threading vs multi-processing?"
        ),
        skills=["Python", "Concurrency"],
        technologies=["Python", "threading", "multiprocessing"],
        expected_concepts=[
            "GIL",
            "Thread Safety",
            "CPU-bound vs IO-bound Tasks",
            "multiprocessing module",
        ],
        has_follow_up=True,
    ),

    create_question(
        role="Python Developer",
        experience_level=ExperienceLevel.FRESHER,
        category=QuestionCategory.ROLE_SPECIFIC,
        difficulty=DifficultyLevel.MEDIUM,
        question_text=(
            "How do Python decorators work? "
            "Write a simple decorator that measures function execution time."
        ),
        skills=["Python", "Functional Programming"],
        technologies=["Python"],
        expected_concepts=[
            "Higher-Order Functions",
            "Closures",
            "functools.wraps",
            "time module",
            "Wrapper Pattern",
        ],
        has_follow_up=False,
    ),
]
