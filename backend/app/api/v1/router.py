from fastapi import APIRouter
from app.api.v1.endpoints import auth, users

api_router = APIRouter()

# Core system endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Plug future business modules here seamlessly:
# from app.modules.billing import router as billing_router
# api_router.include_router(billing_router, prefix="/billing", tags=["billing"])
