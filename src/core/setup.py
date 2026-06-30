from collections.abc import AsyncGenerator, Callable
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import AppSettings, CORSSettings, DatabaseSettings, EnvironmentSettings
from ..database import Base
from ..database import async_engine as engine
from ..middleware.logger_middleware import LoggerMiddleware
from ..models import *  # noqa: F403


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def lifespan_factory(
    settings: DatabaseSettings | AppSettings | CORSSettings | EnvironmentSettings,
    create_tables_on_start: bool = True,
) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
    """Simple lifespan that creates tables during startup."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        if create_tables_on_start:
            await create_tables()
        yield

    return lifespan


def create_application(
    router: APIRouter,
    settings: DatabaseSettings | AppSettings | CORSSettings | EnvironmentSettings,
    create_tables_on_start: bool = True,
    lifespan: Callable[[FastAPI], _AsyncGeneratorContextManager[Any]] | None = None,
    **kwargs: Any,
) -> FastAPI:
    """Create a simple FastAPI application with user routes and basic middleware."""
    if isinstance(settings, AppSettings):
        kwargs.update(
            {
                "title": settings.APP_NAME,
                "description": settings.APP_DESCRIPTION,
                "contact": {"name": settings.CONTACT_NAME, "email": settings.CONTACT_EMAIL},
                "license_info": {"name": settings.LICENSE_NAME},
            }
        )

    if lifespan is None:
        lifespan = lifespan_factory(settings, create_tables_on_start=create_tables_on_start)

    application = FastAPI(lifespan=lifespan, **kwargs)
    application.include_router(router)

    if isinstance(settings, CORSSettings):
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=settings.CORS_METHODS,
            allow_headers=settings.CORS_HEADERS,
        )

    application.add_middleware(LoggerMiddleware)
    return application
