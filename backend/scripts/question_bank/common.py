# backend/scripts/question_bank/common.py
"""
Shared utilities for question bank seed modules.

All role modules import from here. No duplication of factory logic.
"""

import sys
from pathlib import Path

# Ensure the backend package is importable when running scripts directly.
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.models.question_bank import QuestionBank
from app.shared.enums import (
    DifficultyLevel,
    ExperienceLevel,
    QuestionCategory,
    QuestionSource,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_SOURCE: QuestionSource = QuestionSource.MANUAL


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_question(
    *,
    role: str,
    experience_level: ExperienceLevel,
    category: QuestionCategory,
    difficulty: DifficultyLevel,
    question_text: str,
    skills: list[str],
    technologies: list[str],
    expected_concepts: list[str],
    has_follow_up: bool = False,
    source: QuestionSource = DEFAULT_SOURCE,
) -> QuestionBank:
    """
    Create a single QuestionBank ORM instance with full AI metadata.

    All fields are keyword-only to prevent positional argument mistakes.
    """
    return QuestionBank(
        role=role,
        experience_level=experience_level,
        category=category,
        difficulty=difficulty,
        question_text=question_text,
        skills=skills,
        technologies=technologies,
        expected_concepts=expected_concepts,
        has_follow_up=has_follow_up,
        source=source,
    )
