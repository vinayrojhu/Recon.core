import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.rbac import RoleRead

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    role_ids: list[uuid.UUID] = []

class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None
    role_ids: list[uuid.UUID] | None = None

class UserRead(UserBase):
    id: uuid.UUID
    is_superuser: bool
    roles: list[RoleRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
  
