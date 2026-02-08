from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.bookings.models import Booking, BookingStatus
from src.core.time_utils import utc_now


class BookingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, booking_id: int) -> Booking | None:
        result = await self.session.execute(
            select(Booking)
            .where(Booking.id == booking_id)
            .options(selectinload(Booking.user))
        )
        return result.scalar_one_or_none()

    async def list_future_for_user(self, user_id: int) -> list[Booking]:
        now = utc_now()
        result = await self.session.execute(
            select(Booking)
            .where(Booking.user_id == user_id)
            .where(Booking.status == BookingStatus.ACTIVE)
            .where(Booking.start_time >= now)
            .order_by(Booking.start_time)
        )
        return list(result.scalars().all())

    async def has_conflict(
        self,
        table_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: int | None = None,
    ) -> bool:
        stmt = (
            select(Booking.id)
            .where(Booking.table_id == table_id)
            .where(Booking.status == BookingStatus.ACTIVE)
            .where(Booking.start_time < end_time)
            .where(Booking.end_time > start_time)
        )
        if exclude_booking_id is not None:
            stmt = stmt.where(Booking.id != exclude_booking_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        user_id: int,
        table_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> int:
        stmt = (
            insert(Booking)
            .values(
                user_id=user_id,
                table_id=table_id,
                start_time=start_time,
                end_time=end_time,
                status=BookingStatus.ACTIVE,
            )
            .returning(Booking.id)
        )
        result = await self.session.execute(stmt)
        booking_id = result.scalar_one()
        await self.session.commit()
        return booking_id

    async def update_time(
        self,
        booking: Booking,
        start_time: datetime,
        end_time: datetime,
    ) -> Booking:
        booking.start_time = start_time
        booking.end_time = end_time
        await self.session.commit()
        await self.session.refresh(booking)
        return booking

    async def cancel(self, booking: Booking) -> Booking:
        booking.status = BookingStatus.CANCELED
        await self.session.commit()
        await self.session.refresh(booking)
        return booking
