from typing import Optional

from crudadmin import CRUDAdmin
from sqlalchemy.exc import IntegrityError

from ..core.config import EnvironmentOption, settings
from ..core.db.database import async_get_db
from .views import register_admin_views


async def initialize_admin_safely(admin: CRUDAdmin) -> None:
    """Initialize the admin interface while tolerating duplicate initial-admin inserts."""
    try:
        await admin.initialize()
    except IntegrityError as exc:
        message = str(exc).lower()
        if "unique constraint failed" in message and "admin_user.username" in message:
            return
        raise


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
        initial_admin={
            "username": settings.ADMIN_USERNAME,
            "password": settings.ADMIN_PASSWORD,
        }
        if settings.ADMIN_USERNAME and settings.ADMIN_PASSWORD
        else None,
    )

    register_admin_views(admin)

    return admin
