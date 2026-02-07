from uuid import uuid4

from src.auth.models import User
from src.core.security import create_access_token, hash_password
from src.tables.models import Table


def auth_header(user_id: int) -> dict[str, str]:
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


async def create_user(
    session,
    email: str | None = None,
    password: str = "password",
    is_admin: bool = False,
) -> User:
    user = User(
        email=email or f"user-{uuid4()}@example.com",
        hashed_password=hash_password(password),
        full_name="Test User",
        phone_number="100200300",
        is_admin=is_admin,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_table(session, name: str = "T1", seats: int = 2) -> Table:
    table = Table(name=name, seats=seats)
    session.add(table)
    await session.commit()
    await session.refresh(table)
    return table
