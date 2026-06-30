from collections.abc import AsyncGenerator
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from .config import settings


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class TimestampMixin(MappedAsDataclass):
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now(), init=False)
    updated_at: Mapped[datetime] = mapped_column(insert_default=func.now(), onupdate=func.now(), init=False)


DATABASE_URL = settings.POSTGRES_URL or f"{settings.POSTGRES_ASYNC_PREFIX}{settings.POSTGRES_URI}"


async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as db:
        yield db
