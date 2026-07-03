# backend/app/repositories/resume_repository.py
"""
Resume repository — all database access for the Resume domain.

Services must never import SQLAlchemy queries directly. All DB access goes here.
"""

from sqlalchemy.orm import Session

from app.models.resume import Resume


class ResumeRepository:

    @staticmethod
    def create(
        db: Session,
        resume: Resume,
    ) -> Resume:
        """Persist a new Resume record and return it with server-generated fields."""
        try:
            db.add(resume)
            db.commit()
            db.refresh(resume)
            return resume
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_by_id(
        db: Session,
        resume_id: int,
    ) -> Resume | None:
        """Return a Resume by primary key, regardless of owner."""
        return (
            db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

    @staticmethod
    def get_by_id_and_user(
        db: Session,
        resume_id: int,
        user_id: int,
    ) -> Resume | None:
        """
        Return a Resume only if it belongs to user_id.

        Returns None if the record does not exist OR belongs to a different user.
        This prevents information disclosure (same semantics as 404 for both cases).
        """
        return (
            db.query(Resume)
            .filter(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
            .first()
        )

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int,
    ) -> list[Resume]:
        """Return all resumes belonging to user_id, newest first."""
        return (
            db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.id.desc())
            .all()
        )

    @staticmethod
    def save(
        db: Session,
        resume: Resume,
    ) -> Resume:
        """Persist changes to an already-tracked Resume instance."""
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def delete(
        db: Session,
        resume: Resume,
    ) -> None:
        """Hard-delete a Resume record from the database."""
        try:
            db.delete(resume)
            db.commit()
        except Exception:
            db.rollback()
            raise
