"""Service layer handling device registration and listing."""
from datetime import datetime, timezone
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.auth.models import User
from app.modules.devices.models import Device, DeviceCapability
from app.modules.devices.schemas import (
    DeviceCapabilitySchema,
    DeviceItemResponse,
    DeviceListResponse,
    DeviceRegisterRequest,
    DeviceRegisterResponse,
)


class DeviceService:
    """Service handling device lifecycle."""

    @staticmethod
    async def register_device(
        db: AsyncSession,
        current_user: User,
        req: DeviceRegisterRequest,
    ) -> DeviceRegisterResponse:
        """Register or update an existing device identifier for the authenticated user."""
        stmt = (
            select(Device)
            .where(
                Device.user_id == current_user.id,
                Device.device_identifier == req.device_identifier,
            )
            .options(selectinload(Device.capabilities))
        )
        result = await db.execute(stmt)
        device = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if device:
            # Update device metadata
            device.platform = req.platform
            device.device_model = req.device_model
            device.os_version = req.os_version
            device.app_version = req.app_version

            if device.capabilities:
                device.capabilities.supports_network_tracking = req.capabilities.supports_network_tracking
                device.capabilities.supports_app_shielding = req.capabilities.supports_app_shielding
                device.capabilities.has_usage_permission = req.capabilities.has_usage_permission
                device.capabilities.has_screen_time_permission = req.capabilities.has_screen_time_permission
            else:
                capabilities = DeviceCapability(
                    device_id=device.id,
                    supports_network_tracking=req.capabilities.supports_network_tracking,
                    supports_app_shielding=req.capabilities.supports_app_shielding,
                    has_usage_permission=req.capabilities.has_usage_permission,
                    has_screen_time_permission=req.capabilities.has_screen_time_permission,
                )
                db.add(capabilities)
        else:
            # Create new device
            device = Device(
                user_id=current_user.id,
                device_identifier=req.device_identifier,
                platform=req.platform,
                device_model=req.device_model,
                os_version=req.os_version,
                app_version=req.app_version,
            )
            db.add(device)
            await db.flush()

            capabilities = DeviceCapability(
                device_id=device.id,
                supports_network_tracking=req.capabilities.supports_network_tracking,
                supports_app_shielding=req.capabilities.supports_app_shielding,
                has_usage_permission=req.capabilities.has_usage_permission,
                has_screen_time_permission=req.capabilities.has_screen_time_permission,
            )
            db.add(capabilities)

        await db.flush()

        return DeviceRegisterResponse(
            device_id=device.id,
            status="registered",
            registered_at=now,
        )

    @staticmethod
    async def list_devices(
        db: AsyncSession,
        current_user: User,
    ) -> DeviceListResponse:
        """List all active devices owned by the authenticated user."""
        stmt = (
            select(Device)
            .where(Device.user_id == current_user.id)
            .options(selectinload(Device.capabilities))
        )
        result = await db.execute(stmt)
        devices = result.scalars().all()

        device_items = []
        for d in devices:
            caps = None
            if d.capabilities:
                caps = DeviceCapabilitySchema(
                    supports_network_tracking=d.capabilities.supports_network_tracking,
                    supports_app_shielding=d.capabilities.supports_app_shielding,
                    has_usage_permission=d.capabilities.has_usage_permission,
                    has_screen_time_permission=d.capabilities.has_screen_time_permission,
                )
            device_items.append(
                DeviceItemResponse(
                    id=d.id,
                    device_identifier=d.device_identifier,
                    platform=d.platform,
                    device_model=d.device_model,
                    os_version=d.os_version,
                    app_version=d.app_version,
                    last_sync_at=d.last_sync_at,
                    capabilities=caps,
                )
            )

        return DeviceListResponse(devices=device_items)
