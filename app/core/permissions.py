"""Role-based authorization and administrative dependency guards."""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.core.security import decode_token

admin_security_scheme = HTTPBearer(auto_error=False)


async def get_current_admin(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(admin_security_scheme),
) -> dict:
    """Validate admin JWT and return decoded claims including role."""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing administrative authorization credentials",
        )

    token = auth.credentials
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Administrative session token has expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrative session token",
        )

    role = payload.get("role", "admin")
    admin_id = payload.get("admin_id") or payload.get("sub")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing administrative identifier in token",
        )

    return {
        "admin_id": admin_id,
        "email": payload.get("email", ""),
        "role": role,
    }


def require_roles(allowed_roles: List[str]):
    """Enforce that current administrator possesses one of the allowed roles."""
    async def role_checker(admin: dict = Depends(get_current_admin)) -> dict:
        if admin.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of the following roles: {', '.join(allowed_roles)}",
            )
        return admin
    return role_checker


require_super_admin = require_roles(["super_admin"])
require_admin_or_above = require_roles(["super_admin", "admin"])
