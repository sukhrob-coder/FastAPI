from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import router
from .core.config import settings
from .core.setup import create_application, lifespan_factory


@asynccontextmanager
async def lifespan_with_users(app: FastAPI) -> AsyncGenerator[None, None]:
    """Minimal lifespan that only initializes the database tables."""
    async with lifespan_factory(settings)(app):
        yield


app = create_application(router=router, settings=settings, lifespan=lifespan_with_users)
