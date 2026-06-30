from typing import Optional

from crudadmin import CRUDAdmin
from sqlalchemy import Enum
from sqlalchemy.schema import CreateTable

from ..config import EnvironmentOption, settings
from ..database import DATABASE_URL, async_get_db
from .views import register_admin_views


async def initialize_admin_tables(admin: CRUDAdmin) -> None:
    """Create CRUDAdmin tables without creating an initial admin user."""
    db_config = admin.db_config
    tables_to_create = [
        db_config.AdminUser,
        db_config.AdminSession,
    ]

    if db_config.AdminEventLog is not None:
        tables_to_create.append(db_config.AdminEventLog)
    if db_config.AdminAuditLog is not None:
        tables_to_create.append(db_config.AdminAuditLog)

    async with db_config.admin_engine.begin() as conn:
        for model in tables_to_create:
            for column in model.__table__.columns:
                if isinstance(column.type, Enum):
                    await conn.run_sync(column.type.create, checkfirst=True)

        for model in tables_to_create:
            await conn.execute(CreateTable(model.__table__, if_not_exists=True))


def create_admin_interface() -> Optional[CRUDAdmin]:
    """Create and configure the admin interface."""
    if not settings.CRUD_ADMIN_ENABLED:
        return None

    session_backend = "memory"
    redis_config = None

    if settings.CRUD_ADMIN_REDIS_ENABLED:
        session_backend = "redis"
        redis_config = {
            "host": settings.CRUD_ADMIN_REDIS_HOST,
            "port": settings.CRUD_ADMIN_REDIS_PORT,
            "db": settings.CRUD_ADMIN_REDIS_DB,
            "password": settings.CRUD_ADMIN_REDIS_PASSWORD if settings.CRUD_ADMIN_REDIS_PASSWORD != "None" else None,
        }

    admin = CRUDAdmin(
        session=async_get_db,
        SECRET_KEY=settings.SECRET_KEY.get_secret_value(),
        admin_db_url=DATABASE_URL,
        mount_path=settings.CRUD_ADMIN_MOUNT_PATH,
        session_backend=session_backend,
        redis_config=redis_config,
        allowed_ips=settings.CRUD_ADMIN_ALLOWED_IPS_LIST if settings.CRUD_ADMIN_ALLOWED_IPS_LIST else None,
        allowed_networks=settings.CRUD_ADMIN_ALLOWED_NETWORKS_LIST
        if settings.CRUD_ADMIN_ALLOWED_NETWORKS_LIST
        else None,
        max_sessions_per_user=settings.CRUD_ADMIN_MAX_SESSIONS,
        session_timeout_minutes=settings.CRUD_ADMIN_SESSION_TIMEOUT,
        secure_cookies=settings.SESSION_SECURE_COOKIES,
        enforce_https=settings.ENVIRONMENT == EnvironmentOption.PRODUCTION,
        track_events=settings.CRUD_ADMIN_TRACK_EVENTS,
        track_sessions_in_db=settings.CRUD_ADMIN_TRACK_SESSIONS,
    )

    register_admin_views(admin)

    return admin
