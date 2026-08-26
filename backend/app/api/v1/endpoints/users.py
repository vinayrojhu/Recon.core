import uuid
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_permission
from app.core.database import get_db
from app.core.exceptions import AppException, NotFoundError
from app.core.security import get_password_hash
from app.models.audit import AuditLog
from app.models.rbac import Role
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

@router.get("", response_model=ApiResponse[list[UserRead]])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("users:read")),
):
    result = await db.execute(
        select(User).where(User.is_deleted == False).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return ApiResponse(data=list(users))

@router.post("", response_model=ApiResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users:create")),
):
    existing = await db.execute(select(User).where(User.email == user_in.email))
    if existing.scalars().first():
        raise AppException("Email is already registered", status_code=status.HTTP_409_CONFLICT, error_code="USER_EXISTS")

    roles = []
    if user_in.role_ids:
        roles_result = await db.execute(select(Role).where(Role.id.in_(user_in.role_ids)))
        roles = list(roles_result.scalars().all())

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=user_in.is_active,
        roles=roles,
    )
    db.add(user)
    await db.flush()

    db.add(AuditLog(
        user_id=current_user.id,
        action="USER_CREATE",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    ))

    await db.commit()
    await db.refresh(user)
    return ApiResponse(data=user)
  
