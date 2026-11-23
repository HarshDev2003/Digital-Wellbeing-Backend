"""FastAPI router for Authentication endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    return await AuthService.register_user(db, req)


@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with email and password."""
    return await AuthService.login_user(db, req)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a fresh access token."""
    access_token = await AuthService.refresh_access_token(db, req.refresh_token)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve profile of the currently authenticated user."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        timezone=current_user.timezone,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
