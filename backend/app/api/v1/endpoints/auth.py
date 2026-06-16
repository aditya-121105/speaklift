from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
)
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.dependencies.database import get_db
from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register")
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = AuthService.register_user(
            db,
            payload,
        )

        return {
            "message": "User registered successfully",
            "user_id": user.id,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.post("/login")
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return AuthService.login_user(
            db,
            payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        )

@router.get("/me")
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_verified": current_user.is_verified,
    }