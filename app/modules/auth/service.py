"""Service layer handling user authentication and token rotation."""
from datetime import datetime, timedelta, timezone
import hashlib
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import RefreshToken, User
from app.modules.auth.schemas import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)


def _hash_token(token: str) -> str:
    """Compute SHA-256 hash of refresh token string for secure database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    """Core authentication service."""

    @staticmethod
    async def register_user(db: AsyncSession, req: UserRegisterRequest) -> UserRegisterResponse:
        """Register a new user, ensuring email uniqueness."""
        email_clean = req.email.strip().lower()

        # Check existing email
        stmt = select(User).where(User.email == email_clean)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists.",
            )

        hashed_pw = hash_password(req.password)
        new_user = User(
            email=email_clean,
            password_hash=hashed_pw,
            role=req.role or "user",
            timezone=req.timezone,
            is_active=True,
        )
        db.add(new_user)
        await db.flush()

        access_token = create_access_token(
            {"sub": str(new_user.id), "email": new_user.email, "role": new_user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return UserRegisterResponse(
            user_id=new_user.id,
            email=new_user.email,
            role=new_user.role,
            timezone=new_user.timezone,
            access_token=access_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @staticmethod
    async def login_user(db: AsyncSession, req: UserLoginRequest) -> UserLoginResponse:
        """Authenticate user credentials and issue access and rotating refresh tokens."""
        email_clean = req.email.strip().lower()
        stmt = select(User).where(User.email == email_clean)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated",
            )

        access_token = create_access_token(
            {"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        raw_refresh_token = str(uuid.uuid4())
        token_hash = _hash_token(raw_refresh_token)
        refresh_expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=refresh_expires,
            revoked=False,
        )
        db.add(refresh_record)
        await db.flush()

        return UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=raw_refresh_token,
            role=user.role,
        )

    @staticmethod
    async def refresh_access_token(db: AsyncSession, raw_refresh_token: str) -> str:
        """Validate refresh token and issue a fresh access token."""
        token_hash = _hash_token(raw_refresh_token)
        now = datetime.now(timezone.utc)

        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > now,
        )
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # Retrieve user
        user_stmt = select(User).where(User.id == record.user_id, User.is_active == True)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Associated user account is deactivated or not found",
            )

        access_token = create_access_token(
            {"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return access_token
