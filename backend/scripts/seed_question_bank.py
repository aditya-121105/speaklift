# backend/scripts/seed_question_bank.py
"""
Question Bank seed orchestrator.

Responsibilities:
  1. Import question collections from each role module.
  2. Combine them into a single list.
  3. Insert into the database.
  4. Print an insertion summary.

No interview questions live in this file.
To add a new role: create backend/scripts/question_bank/<role>.py
and import its QUESTIONS list below.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.models.question_bank import QuestionBank

# ------------------------------------------------------------------
# Role collections
# Import QUESTIONS from each role module.
# ------------------------------------------------------------------
from question_bank.backend_developer import QUESTIONS as BACKEND_DEVELOPER_QUESTIONS
from question_bank.python_developer import QUESTIONS as PYTHON_DEVELOPER_QUESTIONS
from question_bank.ai_ml_engineer import QUESTIONS as AI_ML_ENGINEER_QUESTIONS
from question_bank.data_scientist import QUESTIONS as DATA_SCIENTIST_QUESTIONS
from question_bank.cloud_engineer import QUESTIONS as CLOUD_ENGINEER_QUESTIONS
from question_bank.devops_engineer import QUESTIONS as DEVOPS_ENGINEER_QUESTIONS


def _collect_all_questions() -> list[QuestionBank]:
    """Combine all role question collections into one list."""
    return [
        *BACKEND_DEVELOPER_QUESTIONS,
        *PYTHON_DEVELOPER_QUESTIONS,
        *AI_ML_ENGINEER_QUESTIONS,
        *DATA_SCIENTIST_QUESTIONS,
        *CLOUD_ENGINEER_QUESTIONS,
        *DEVOPS_ENGINEER_QUESTIONS,
    ]


def _print_summary(questions: list[QuestionBank]) -> None:
    """Print a breakdown of inserted questions by role."""
    from collections import Counter
    counts: Counter[str] = Counter(q.role for q in questions)
    print("\n--- Seed Summary ---")
    for role, count in sorted(counts.items()):
        print(f"  {role}: {count} question(s)")
    print(f"  TOTAL: {len(questions)} question(s)")
    print("--------------------\n")


def seed_questions() -> None:
    db = SessionLocal()
    try:
        questions = _collect_all_questions()
        db.add_all(questions)
        db.commit()
        print(f"Successfully inserted {len(questions)} questions.")
        _print_summary(questions)
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_questions()