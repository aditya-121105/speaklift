# backend/scripts/seed_question_bank.py
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.db.session import SessionLocal

from app.repositories.interview_session_repository import (
    InterviewSessionRepository,
)

from app.services.interview_question_generator_service import (
    InterviewQuestionGeneratorService,
)


def main():

    db = SessionLocal()

    try:

        interview_session = (
            InterviewSessionRepository.get_by_id(
                db,
                1,
            )
        )

        if not interview_session:

            print(
                "Interview session not found."
            )

            return

        questions = (
            InterviewQuestionGeneratorService
            .generate_questions(
                db,
                interview_session,
            )
        )

        print(
            f"Generated {len(questions)} questions."
        )

        for question in questions:

            print(
                f"{question.question_order}. "
                f"{question.question_text}"
            )

    finally:

        db.close()


if __name__ == "__main__":
    main()