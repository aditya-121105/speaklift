# backend/app/api/v1/endpoints/resumes.py
"""
Resume endpoints — thin HTTP layer only.

Routes
------
POST   /resumes/upload          Upload a new resume (multipart/form-data)
GET    /resumes                 List all resumes for the authenticated user
GET    /resumes/{resume_id}     Get metadata for a specific resume
DELETE /resumes/{resume_id}     Delete a resume and its file

All business logic is in ResumeService.
All DB access is in ResumeRepository.
Endpoints are intentionally thin — no business logic lives here.
"""

import logging

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.storage import StorageBackend
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.dependencies.storage import get_storage
from app.models.user import User
from app.schemas.resume import ResumeListResponse, ResumeResponse
from app.services.resume_service import ResumeService

from app.dependencies.ai import (
    get_document_extractor,
    get_nlp_pipeline,
    get_entity_validator,
    get_profile_builder,
)
from app.ai.document_processing.services import DocumentExtractionService
from app.ai.nlp.pipeline import NLPPipeline
from app.ai.nlp.validators.entity_validator import EntityValidator
from app.services.candidate_profile.builder import CandidateProfileBuilder

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=201,
    summary="Upload a resume",
    description=(
        "Upload a PDF or DOCX resume file using multipart/form-data. "
        "Maximum file size is governed by MAX_RESUME_SIZE_MB. "
        "Only PDF and DOCX are accepted."
    ),
)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageBackend = Depends(get_storage),
    document_extractor: DocumentExtractionService = Depends(get_document_extractor),
    nlp_pipeline: NLPPipeline = Depends(get_nlp_pipeline),
    entity_validator: EntityValidator = Depends(get_entity_validator),
    profile_builder: CandidateProfileBuilder = Depends(get_profile_builder),
) -> ResumeResponse:
    # Read file bytes here (async). The synchronous service receives raw bytes.
    file_data = await file.read()

    resume = ResumeService.upload_resume(
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

    return ResumeResponse.model_validate(resume)


@router.get(
    "",
    response_model=ResumeListResponse,
    summary="List resumes",
    description="Return all resumes uploaded by the authenticated user, newest first.",
)
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeListResponse:
    resumes = ResumeService.get_user_resumes(db, current_user.id)
    return ResumeListResponse(
        resumes=[ResumeResponse.model_validate(r) for r in resumes],
        total=len(resumes),
    )


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Get resume metadata",
    description="Return metadata for a specific resume owned by the authenticated user.",
)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeResponse:
    resume = ResumeService.get_resume(db, resume_id, current_user.id)
    return ResumeResponse.model_validate(resume)


@router.get(
    "/{resume_id}/download",
    summary="Download resume file",
    description=(
        "Stream the resume file to the client. "
        "Note: this endpoint is only meaningful for LOCAL storage. "
        "A future S3 implementation will return a presigned URL instead."
    ),
)
def download_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageBackend = Depends(get_storage),
) -> FileResponse:
    resume = ResumeService.get_resume(db, resume_id, current_user.id)
    file_path = storage.get_absolute_path(resume.storage_path)

    return FileResponse(
        path=str(file_path),
        filename=resume.original_filename,
        media_type=resume.mime_type,
    )


@router.delete(
    "/{resume_id}",
    status_code=204,
    summary="Delete a resume",
    description=(
        "Delete the resume file from storage and remove the database record. "
        "Returns 204 No Content on success."
    ),
)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageBackend = Depends(get_storage),
) -> None:
    ResumeService.delete_resume(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
        storage=storage,
    )
