from fastapi import APIRouter

from .health import router as health_router
from .users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(health_router)
router.include_router(users_router)
