import uuid
from pydantic import BaseModel, ConfigDict

class PermissionBase(BaseModel):
    name: str
    description: str | None = None

class PermissionRead(PermissionBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class RoleBase(BaseModel):
    name: str
    description: str | None = None

class RoleCreate(RoleBase):
    permission_ids: list[uuid.UUID] = []

class RoleRead(RoleBase):
    id: uuid.UUID
    permissions: list[PermissionRead] = []
    model_config = ConfigDict(from_attributes=True)
  
