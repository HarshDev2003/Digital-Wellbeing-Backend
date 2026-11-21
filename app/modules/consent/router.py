"""FastAPI router for User Consent endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.consent.schemas import UserConsentRequest, UserConsentResponse
from app.modules.consent.service import ConsentService

router = APIRouter(prefix="/consent", tags=["Consent"])


@router.post("", response_model=UserConsentResponse, status_code=status.HTTP_200_OK)
async def record_consent(
    req: UserConsentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record explicit user consent or revocation for data tracking and AI analysis."""
    return await ConsentService.record_consent(db, current_user, req)
