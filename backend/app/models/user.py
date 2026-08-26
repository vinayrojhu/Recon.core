from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import CoreBaseModel
from app.models.rbac import Role, user_roles

class User(CoreBaseModel):
    __tablename__ = "core_users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    roles: Mapped[list[Role]] = relationship(
        "Role", secondary=user_roles, lazy="selectin"
    )
  
