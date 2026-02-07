from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings.models import Booking, BookingStatus
from src.tables.models import Table


class TableRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, table_id: int) -> Table | None:
        result = await self.session.execute(select(Table).where(Table.id == table_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Table]:
        result = await self.session.execute(select(Table).order_by(Table.id))
        return list(result.scalars().all())

    async def get_available(
        self,
        start_time: datetime,
        end_time: datetime,
        seats: int | None = None,
    ) -> list[Table]:
        busy_tables = (
            select(Booking.table_id)
            .where(Booking.status == BookingStatus.ACTIVE)
            .where(Booking.start_time < end_time)
            .where(Booking.end_time > start_time)
        )
        stmt = select(Table).where(Table.id.not_in(busy_tables))
        if seats is not None:
            stmt = stmt.where(Table.seats >= seats)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, name: str, seats: int) -> int:
        stmt = insert(Table).values(name=name, seats=seats).returning(Table.id)
        result = await self.session.execute(stmt)
        table_id = result.scalar_one()
        await self.session.commit()
        return table_id

    async def update(
        self,
        table: Table,
        name: str | None = None,
        seats: int | None = None,
    ) -> Table:
        if name is not None:
            table.name = name
        if seats is not None:
            table.seats = seats
        await self.session.commit()
        await self.session.refresh(table)
        return table

    async def delete(self, table: Table) -> None:
        await self.session.delete(table)
        await self.session.commit()
