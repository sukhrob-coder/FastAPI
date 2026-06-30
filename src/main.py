from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from .admin.initialize import create_admin_interface, initialize_admin_tables
from .auth.router import router as auth_router
from .config import settings
from .core.setup import create_application, lifespan_factory
from .health.router import router as health_router
from .posts.router import router as posts_router
from .tasks.router import router as tasks_router
from .users.router import router as users_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(posts_router)
router.include_router(tasks_router)

admin_interface = create_admin_interface()


@asynccontextmanager
async def lifespan_with_users(app: FastAPI) -> AsyncGenerator[None, None]:
    """Minimal lifespan that only initializes the database tables."""
    async with lifespan_factory(settings)(app):
        if admin_interface is not None:
            await initialize_admin_tables(admin_interface)
        yield


app = create_application(router=router, settings=settings, lifespan=lifespan_with_users)

if admin_interface is not None:
    app.mount(settings.CRUD_ADMIN_MOUNT_PATH, admin_interface.app)
