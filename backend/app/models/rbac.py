from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import CoreBaseModel

role_permissions = Table(
    "core_role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("core_roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("core_permissions.id", ondelete="CASCADE"), primary_key=True),
)

user_roles = Table(
    "core_user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("core_users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("core_roles.id", ondelete="CASCADE"), primary_key=True),
)

class Permission(CoreBaseModel):
    __tablename__ = "core_permissions"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

class Role(CoreBaseModel):
    __tablename__ = "core_roles"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    permissions: Mapped[list[Permission]] = relationship(
        "Permission", secondary=role_permissions, lazy="selectin"
    )
  
