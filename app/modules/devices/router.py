"""FastAPI router for Device endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.devices.schemas import (
    DeviceListResponse,
    DeviceRegisterRequest,
    DeviceRegisterResponse,
)
from app.modules.devices.service import DeviceService

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/register", response_model=DeviceRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    req: DeviceRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register or update a companion mobile device for the authenticated user."""
    return await DeviceService.register_device(db, current_user, req)


@router.get("", response_model=DeviceListResponse, status_code=status.HTTP_200_OK)
async def list_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all companion devices associated with the current user."""
    return await DeviceService.list_devices(db, current_user)
