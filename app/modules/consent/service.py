"""Service layer handling user consent audit trail."""
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
from app.modules.consent.models import UserConsent
from app.modules.consent.schemas import UserConsentRequest, UserConsentResponse


class ConsentService:
    """Service handling audit trail of explicit user consent."""

    @staticmethod
    async def record_consent(
        db: AsyncSession,
        current_user: User,
        req: UserConsentRequest,
    ) -> UserConsentResponse:
        """Append an immutable audit entry recording user consent grant or revocation."""
        consent_record = UserConsent(
            user_id=current_user.id,
            consent_type=req.consent_type,
            policy_version=req.policy_version,
            granted=req.granted,
        )
        db.add(consent_record)
        await db.flush()

        return UserConsentResponse(
            status="recorded",
            consent_id=consent_record.id,
            timestamp=consent_record.timestamp,
        )
