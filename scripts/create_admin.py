import asyncio
import os

from sqlalchemy import select

from src.auth.models import User
from src.bookings import models as _booking_models  # noqa: F401
from src.core.security import hash_password
from src.db.session import SessionFactory
from src.tables import models as _table_models  # noqa: F401


async def ensure_admin() -> None:
    email = os.getenv("ADMIN_EMAIL", "admin@booking.com")
    password = os.getenv("ADMIN_PASSWORD", "12345678")
    full_name = os.getenv("ADMIN_FULL_NAME", "Admin")
    phone_number = os.getenv("ADMIN_PHONE_NUMBER", "88005553535")

    async with SessionFactory() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            if not user.is_admin:
                user.is_admin = True
                await session.commit()
            return
        session.add(
            User(
                email=email,
                hashed_password=hash_password(password),
                full_name=full_name,
                phone_number=phone_number,
                is_admin=True,
            )
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(ensure_admin())
