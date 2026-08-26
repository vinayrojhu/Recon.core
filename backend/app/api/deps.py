import uuid
from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AuthenticationFailedError, PermissionDeniedError
from app.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise AuthenticationFailedError("Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationFailedError("Could not validate credentials")
    except JWTError:
        raise AuthenticationFailedError("Invalid or expired credentials")

    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id), User.is_deleted == False)
    )
    user = result.scalars().first()

    if not user:
        raise AuthenticationFailedError("User does not exist")
    if not user.is_active:
        raise AuthenticationFailedError("User is deactivated")

    return user

def require_permission(required_permission: str) -> Callable:
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        user_permissions = {
            perm.name
            for role in current_user.roles
            for perm in role.permissions
        }

        if required_permission not in user_permissions:
            raise PermissionDeniedError(
                f"Missing required permission: '{required_permission}'"
            )
        return current_user

    return permission_checker
  
