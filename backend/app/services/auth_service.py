from sqlalchemy.orm import Session
from app.core.security import (
    create_access_token,
    verify_password,
)
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)

from app.core.security import hash_password
from app.models.profile import Profile
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest


class AuthService:

    @staticmethod
    def register_user(
        db: Session,
        payload: RegisterRequest,
    ) -> User:

        existing_user = UserRepository.get_by_email(
            db,
            payload.email,
        )

        if existing_user:
            raise ValueError(
                "Email already registered"
            )

        user = User(
            email=payload.email,
            password_hash=hash_password(
                payload.password
            ),
            is_active=True,
            is_verified=False,
        )

        db.add(user)
        db.flush()

        profile = Profile(
            user_id=user.id,
            full_name=payload.full_name,
        )

        db.add(profile)

        db.commit()

        db.refresh(user)

        return user

    @staticmethod
    def login_user(
        db: Session,
        payload: LoginRequest,
    ) -> TokenResponse:

        user = UserRepository.get_by_email(
            db,
            payload.email,
        )

        if not user:
            raise ValueError(
                "Invalid email or password"
            )

        if not verify_password(
            payload.password,
            user.password_hash,
        ):
            raise ValueError(
                "Invalid email or password"
            )

        access_token = create_access_token(
            subject=str(user.id),
        )

        return TokenResponse(
            access_token=access_token,
        )