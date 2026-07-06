# backend/app/repositories/job_description_repository.py
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_description import JobDescription


class JobDescriptionRepository:
    """Repository for JobDescription database operations."""

    @staticmethod
    def create(db: Session, job_description: JobDescription) -> JobDescription:
        db.add(job_description)
        db.commit()
        db.refresh(job_description)
        return job_description

    @staticmethod
    def get_by_id_and_user(db: Session, job_description_id: int, user_id: int) -> JobDescription | None:
        stmt = select(JobDescription).where(
            JobDescription.id == job_description_id,
            JobDescription.user_id == user_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_all_for_user(db: Session, user_id: int) -> list[JobDescription]:
        stmt = select(JobDescription).where(JobDescription.user_id == user_id)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def delete(db: Session, job_description: JobDescription) -> None:
        db.delete(job_description)
        db.commit()
