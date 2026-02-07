from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        phone_number: str,
    ) -> int:
        stmt = (
            insert(User)
            .values(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                phone_number=phone_number,
            )
            .returning(User.id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()
