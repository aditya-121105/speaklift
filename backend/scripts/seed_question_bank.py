# backend/scripts/seed_question_bank.py
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)
from app.db.session import SessionLocal

from app.models.question_bank import (
    QuestionBank,
)

from app.shared.enums import (
    DifficultyLevel,
    ExperienceLevel,
    QuestionCategory,
    QuestionSource,
)


def seed_questions():

    db = SessionLocal()

    try:

        questions = [

            # =========================
            # INTRODUCTION
            # =========================

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.INTRODUCTION,
                difficulty=DifficultyLevel.EASY,
                question_text="Tell me about yourself.",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.INTRODUCTION,
                difficulty=DifficultyLevel.EASY,
                question_text="Why do you want to become a backend developer?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.INTRODUCTION,
                difficulty=DifficultyLevel.EASY,
                question_text="What technologies have you worked with so far?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.INTRODUCTION,
                difficulty=DifficultyLevel.EASY,
                question_text="What are your strengths as a developer?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.INTRODUCTION,
                difficulty=DifficultyLevel.EASY,
                question_text="What are your career goals?",
                source=QuestionSource.MANUAL,
            ),

            # =========================
            # PROJECT
            # =========================

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.PROJECT,
                difficulty=DifficultyLevel.EASY,
                question_text="Tell me about a backend project you have worked on.",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.PROJECT,
                difficulty=DifficultyLevel.EASY,
                question_text="What was the biggest challenge in your project?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.PROJECT,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="Why did you choose your project's architecture?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.PROJECT,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="How would you improve your project if you had more time?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.PROJECT,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="Describe your contribution to the project.",
                source=QuestionSource.MANUAL,
            ),

            # =========================
            # TECHNICAL
            # =========================

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.EASY,
                question_text="What is Flask?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.EASY,
                question_text="What is a REST API?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.EASY,
                question_text="What is JWT and why is it used?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.EASY,
                question_text="What is the difference between GET and POST requests?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="What is SQLAlchemy?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="What is database normalization?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="What is a database transaction?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="Explain authentication and authorization.",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.HARD,
                question_text="What are database indexes and why are they used?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.HARD,
                question_text="Explain the request lifecycle in a web application.",
                source=QuestionSource.MANUAL,
            ),

            # =========================
            # BEHAVIORAL
            # =========================

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.BEHAVIORAL,
                difficulty=DifficultyLevel.EASY,
                question_text="Describe a difficult problem you solved.",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.BEHAVIORAL,
                difficulty=DifficultyLevel.EASY,
                question_text="How do you handle deadlines?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.BEHAVIORAL,
                difficulty=DifficultyLevel.EASY,
                question_text="How do you learn a new technology?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.BEHAVIORAL,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="Tell me about a time you worked in a team.",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.BEHAVIORAL,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="Describe a situation where you made a mistake and how you handled it.",
                source=QuestionSource.MANUAL,
            ),

            # =========================
            # ROLE SPECIFIC
            # =========================

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.ROLE_SPECIFIC,
                difficulty=DifficultyLevel.EASY,
                question_text="Why is backend development important in modern applications?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.ROLE_SPECIFIC,
                difficulty=DifficultyLevel.EASY,
                question_text="How would you design an API for a todo application?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.ROLE_SPECIFIC,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="What factors do you consider when designing a database schema?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.ROLE_SPECIFIC,
                difficulty=DifficultyLevel.MEDIUM,
                question_text="How would you secure a backend API?",
                source=QuestionSource.MANUAL,
            ),

            QuestionBank(
                role="Backend Developer",
                experience_level=ExperienceLevel.FRESHER,
                category=QuestionCategory.ROLE_SPECIFIC,
                difficulty=DifficultyLevel.HARD,
                question_text="How would you scale a backend service handling millions of requests?",
                source=QuestionSource.MANUAL,
            ),
        ]

        db.add_all(questions)

        db.commit()

        print(
            f"Successfully inserted {len(questions)} questions."
        )

    except Exception as e:

        db.rollback()

        print(
            f"Error: {e}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    seed_questions()