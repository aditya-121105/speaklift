# backend/app/api/v1/endpoints/job_descriptions.py
import logging

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.storage import StorageBackend
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.dependencies.storage import get_storage
from app.models.user import User
from app.schemas.job_description import JobDescriptionListResponse, JobDescriptionResponse
from app.services.job_description_service import JobDescriptionService

from app.dependencies.ai import (
    get_document_extractor,
    get_jd_nlp_pipeline,
    get_jd_entity_validator,
    get_job_profile_builder,
)
from app.ai.document_processing.services import DocumentExtractionService
from app.ai.nlp.pipeline import NLPPipeline
from app.ai.nlp.validators.entity_validator import EntityValidator
from app.services.job_profile.builder import JobProfileBuilder

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/job-descriptions",
    tags=["Job Descriptions"],
)


@router.post(
    "/upload",
    response_model=JobDescriptionResponse,
    status_code=201,
)
async def upload_job_description(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageBackend = Depends(get_storage),
    document_extractor: DocumentExtractionService = Depends(get_document_extractor),
    nlp_pipeline: NLPPipeline = Depends(get_jd_nlp_pipeline),
    entity_validator: EntityValidator = Depends(get_jd_entity_validator),
    profile_builder: JobProfileBuilder = Depends(get_job_profile_builder),
) -> JobDescriptionResponse:
    file_data = await file.read()

    jd = JobDescriptionService.upload_job_description(
        db=db,
        user_id=current_user.id,
        filename=file.filename or "",
        content_type=file.content_type,
        file_data=file_data,
        storage=storage,
        document_extractor=document_extractor,
        nlp_pipeline=nlp_pipeline,
        entity_validator=entity_validator,
        profile_builder=profile_builder,
    )

    return JobDescriptionResponse.model_validate(jd)


@router.get(
    "",
    response_model=JobDescriptionListResponse,
)
def list_job_descriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionListResponse:
    from app.repositories.job_description_repository import JobDescriptionRepository
    jds = JobDescriptionRepository.get_all_for_user(db, current_user.id)
    return JobDescriptionListResponse(
        job_descriptions=[JobDescriptionResponse.model_validate(j) for j in jds],
        total=len(jds),
    )


@router.get(
    "/{job_description_id}",
    response_model=JobDescriptionResponse,
)
def get_job_description(
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionResponse:
    jd = JobDescriptionService.get_job_description(db, job_description_id, current_user.id)
    return JobDescriptionResponse.model_validate(jd)


@router.delete(
    "/{job_description_id}",
    status_code=204,
)
def delete_job_description(
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageBackend = Depends(get_storage),
) -> None:
    JobDescriptionService.delete_job_description(
        db=db,
        job_description_id=job_description_id,
        user_id=current_user.id,
        storage=storage,
    )
