from contextlib import asynccontextmanager
from asgi_correlation_id import CorrelationIdMiddleware as CoreCorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import setup_logging
from app.core.security import get_password_hash
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.models.rbac import Permission, Role
from app.models.user import User
import structlog

setup_logging()
logger = structlog.get_logger(__name__)

async def seed_initial_rbac():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL))
        if not result.scalars().first():
            logger.info("Seeding initial superuser and base RBAC configuration...")
            perm_users_read = Permission(name="users:read", description="List users")
            perm_users_create = Permission(name="users:create", description="Create users")
            perm_users_update = Permission(name="users:update", description="Update users")
            perm_users_delete = Permission(name="users:delete", description="Delete users")
            
            db.add_all([perm_users_read, perm_users_create, perm_users_update, perm_users_delete])
            await db.flush()

            admin_role = Role(
                name="Platform Admin",
                description="Unrestricted system administrator",
                permissions=[perm_users_read, perm_users_create, perm_users_update, perm_users_delete]
            )
            db.add(admin_role)
            await db.flush()

            superuser = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                full_name="Root Administrator",
                is_superuser=True,
                is_active=True,
                roles=[admin_role],
            )
            db.add(superuser)
            await db.commit()
            logger.info("Superuser seed complete.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Platform Core Engine...")
    await seed_initial_rbac()
    yield
    logger.info("Shutting down Platform Core Engine and releasing resources...")
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

# Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health/live", tags=["system"])
async def liveness_probe():
    return {"status": "UP"}

@app.get("/health/ready", tags=["system"])
async def readiness_probe():
    async with engine.connect() as conn:
        await conn.execute(select(1))
    return {"status": "READY", "database": "CONNECTED"}
  
