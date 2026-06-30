import asyncio
import logging

import bcrypt
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.config import settings
from src.database import local_session
from src.users.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def create_or_update_app_superuser(session: AsyncSession, hashed_password: str) -> None:
    name = settings.ADMIN_NAME
    email = settings.ADMIN_EMAIL
    username = settings.ADMIN_USERNAME

    query = select(User).where(or_(User.email == email, User.username == username))
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            name=name,
            email=email,
            username=username,
            hashed_password=hashed_password,
            profile_image_url=None,
            is_superuser=True,
        )
        session.add(user)
        logger.info("Application superuser %s created successfully.", username)
        return

    user.name = name
    user.hashed_password = hashed_password
    user.is_superuser = True
    logger.info("Application superuser %s already exists; password synced.", username)


async def create_or_update_crudadmin_user(session: AsyncSession, hashed_password: str) -> None:
    username = settings.ADMIN_USERNAME

    await session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS admin_user (
                id SERIAL PRIMARY KEY,
                username VARCHAR(20) UNIQUE NOT NULL,
                hashed_password VARCHAR NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE,
                is_superuser BOOLEAN DEFAULT true NOT NULL
            )
            """
        )
    )
    await session.execute(text("ALTER TABLE admin_user ALTER COLUMN created_at SET DEFAULT now()"))

    result = await session.execute(text("SELECT id FROM admin_user WHERE username = :username"), {"username": username})
    admin_user_id = result.scalar_one_or_none()

    if admin_user_id is None:
        await session.execute(
            text(
                """
                INSERT INTO admin_user (username, hashed_password, created_at, is_superuser)
                VALUES (:username, :hashed_password, now(), true)
                """
            ),
            {"username": username, "hashed_password": hashed_password},
        )
        logger.info("CRUDAdmin user %s created successfully.", username)
        return

    await session.execute(
        text(
            """
            UPDATE admin_user
            SET hashed_password = :hashed_password,
                is_superuser = true,
                updated_at = now()
            WHERE id = :admin_user_id
            """
        ),
        {"admin_user_id": admin_user_id, "hashed_password": hashed_password},
    )
    logger.info("CRUDAdmin user %s already exists; password synced.", username)


async def create_first_user(session: AsyncSession) -> None:
    try:
        hashed_password = get_password_hash(settings.ADMIN_PASSWORD)

        await create_or_update_app_superuser(session, hashed_password)
        await create_or_update_crudadmin_user(session, hashed_password)
        await session.commit()

    except Exception as e:
        await session.rollback()
        logger.error("Error creating admin user: %s", e)
        raise


async def main():
    async with local_session() as session:
        await create_first_user(session)


if __name__ == "__main__":
    asyncio.run(main())
