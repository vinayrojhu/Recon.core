import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AuthenticationFailedError, AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, Token
from app.schemas.response import ApiResponse
from app.schemas.user import UserRead

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == form_data.username, User.is_deleted == False)
    )
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AuthenticationFailedError("Incorrect email or password")
    if not user.is_active:
        raise AuthenticationFailedError("Account is inactive")

    permissions = list({
        perm.name
        for role in user.roles
        for perm in role.permissions
    })

    access_token = create_access_token(user.id, permissions)
    refresh_token = create_refresh_token(user.id)

    db.add(AuditLog(
        user_id=user.id,
        action="AUTH_LOGIN_SUCCESS",
        resource_type="auth",
        ip_address=request.client.host if request.client else None,
    ))

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        data = jwt.decode(payload.refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        if data.get("type") != "refresh":
            raise AuthenticationFailedError("Invalid token type")
        user_id = data.get("sub")
    except JWTError:
        raise AuthenticationFailedError("Invalid or expired refresh token")

    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id), User.is_deleted == False)
    )
    user = result.scalars().first()
    if not user or not user.is_active:
        raise AuthenticationFailedError("User inactive or revoked")

    permissions = list({
        perm.name
        for role in user.roles
        for perm in role.permissions
    })

    return Token(
        access_token=create_access_token(user.id, permissions),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )

@router.get("/me", response_model=ApiResponse[UserRead])
async def read_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(data=current_user)
  
