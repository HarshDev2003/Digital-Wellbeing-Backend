"""Admin User Seeding Script.

Seeds or updates an administrative user account in the database (Supabase/PostgreSQL)
with Argon2id password hashing and active platform consents.

Usage:
    uv run python scripts/seed_admin.py
    uv run python scripts/seed_admin.py --email admin@example.com --password "SecurePass123!" --timezone "America/New_York"
"""
import argparse
import asyncio
import os
import sys
import uuid
from sqlalchemy import select

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import AsyncSessionLocal, engine
from app.core.security import create_access_token, hash_password
from app.modules.auth.models import User, RefreshToken
from app.modules.consent.models import UserConsent
from app.modules.devices.models import Device, DeviceCapability
from app.modules.goals_limits.models import AppCategory, UsageGoal, AppLimit, AppLimitViolation
from app.modules.usage_ingestion.models import AppUsageEvent, ScreenActivityEvent
from app.modules.usage_processing.models import DailyUsageSummary, AppDailySummary


async def seed_admin(email: str, password: str, timezone: str, role: str = "admin") -> None:
    """Create or update an administrative user account."""
    print(f"Connecting to database and seeding admin: {email} (role: {role})...")

    async with AsyncSessionLocal() as session:
        # Check if user already exists
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        password_hash = hash_password(password)

        if user:
            print(f"[!] User with email '{email}' already exists. Updating credentials...")
            user.password_hash = password_hash
            user.timezone = timezone
            user.role = role
            user.is_active = True
            action = "UPDATED"
        else:
            user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=password_hash,
                timezone=timezone,
                role=role,
                is_active=True,
            )
            session.add(user)
            await session.flush()
            action = "CREATED"

        # Grant standard consents so admin has full platform data collection access
        consent_types = ["DATA_COLLECTION", "ANALYTICS", "AI_COACHING"]
        for c_type in consent_types:
            consent_stmt = select(UserConsent).where(
                UserConsent.user_id == user.id,
                UserConsent.consent_type == c_type,
            )
            c_res = await session.execute(consent_stmt)
            existing_consent = c_res.scalar_one_or_none()

            if existing_consent:
                existing_consent.granted = True
                existing_consent.policy_version = "1.0.0"
            else:
                new_consent = UserConsent(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    consent_type=c_type,
                    policy_version="1.0.0",
                    granted=True,
                )
                session.add(new_consent)

        await session.commit()
        await session.refresh(user)

        user_id = str(user.id)

    # Dispose connection pool to cleanly terminate
    await engine.dispose()

    # Generate an admin access token for direct API testing
    admin_token = create_access_token({
        "sub": user_id,
        "admin_id": user_id,
        "email": email,
        "role": "admin",
    })

    border = "=" * 60
    print(f"\n{border}")
    print(f" [SUCCESS] Admin User {action} Successfully")
    print(f"{border}")
    print(f" User ID   : {user_id}")
    print(f" Email     : {email}")
    print(f" Password  : {password}")
    print(f" Timezone  : {timezone}")
    print(f" Consents  : DATA_COLLECTION, ANALYTICS, AI_COACHING (Granted)")
    print(f"{border}")
    print("\n[Option A] Authenticate via API Login:")
    print("curl -X POST http://localhost:8000/api/v1/auth/login \\")
    print('  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"email": "{email}", "password": "{password}"}}\'')
    print("\n[Option B] Instant Admin Bearer Token (ready to use):")
    print(f"Bearer {admin_token}")
    print(f"\nTest Admin Dashboard:")
    print("curl -X GET http://localhost:8000/api/v1/admin/dashboard/overview \\")
    print(f'  -H "Authorization: Bearer {admin_token}"')
    print(f"{border}\n")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Seed administrative user in Digital Wellbeing platform.")
    parser.add_argument(
        "--email",
        type=str,
        default=os.getenv("ADMIN_EMAIL", "admin@digitalwellbeing.com"),
        help="Admin user email address (default: admin@digitalwellbeing.com or ADMIN_EMAIL env)",
    )
    parser.add_argument(
        "--password",
        type=str,
        default=os.getenv("ADMIN_PASSWORD", "Admin@123456"),
        help="Admin user password (default: Admin@123456 or ADMIN_PASSWORD env)",
    )
    parser.add_argument(
        "--timezone",
        type=str,
        default=os.getenv("ADMIN_TIMEZONE", "UTC"),
        help="Admin user timezone (default: UTC or ADMIN_TIMEZONE env)",
    )
    parser.add_argument(
        "--role",
        type=str,
        choices=["admin", "user"],
        default=os.getenv("ADMIN_ROLE", "admin"),
        help="User role (default: admin)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(seed_admin(email=args.email, password=args.password, timezone=args.timezone, role=args.role))
