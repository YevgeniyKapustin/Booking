from datetime import date, datetime, time, timedelta

from src.bookings.models import Booking
from src.bookings.repositories import BookingRepository
from src.core.errors import BusinessError, ForbiddenError, NotFoundError
from src.core.logging_decorators import log_service
from src.tables.repositories import TableRepository
from src.tasks.tasks import send_booking_reminder


class BookingService:
    def __init__(self, bookings: BookingRepository, tables: TableRepository) -> None:
        self.bookings = bookings
        self.tables = tables

    @log_service
    async def list_my_bookings(self, user_id: int) -> list[Booking]:
        return await self.bookings.list_future_for_user(user_id)

    @log_service
    async def create_booking(
        self,
        user_id: int,
        table_id: int,
        target_date: date,
        target_time: time,
    ) -> Booking:
        target_time = self._normalize_time(target_time)
        start_time = datetime.combine(target_date, target_time)
        end_time = start_time + timedelta(hours=2)
        self._ensure_within_working_hours(start_time, end_time)
        self._ensure_same_day(start_time, end_time)
        await self._ensure_table_exists(table_id)
        await self._ensure_slot_available(table_id, start_time, end_time)
        booking_id = await self.bookings.create(user_id, table_id, start_time, end_time)
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        self._schedule_reminder(booking)
        return booking

    @log_service
    async def update_booking_time(
        self,
        booking_id: int,
        user_id: int,
        target_date: date,
        target_time: time,
    ) -> Booking:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        if booking.user_id != user_id:
            raise ForbiddenError("You cannot modify this booking")
        target_time = self._normalize_time(target_time)
        start_time = datetime.combine(target_date, target_time)
        end_time = start_time + timedelta(hours=2)
        self._ensure_within_working_hours(start_time, end_time)
        self._ensure_same_day(start_time, end_time)
        await self._ensure_slot_available(
            booking.table_id, start_time, end_time, booking.id
        )
        booking = await self.bookings.update_time(booking, start_time, end_time)
        self._schedule_reminder(booking)
        return booking

    @log_service
    async def cancel_booking(self, booking_id: int, user_id: int) -> Booking:
        booking = await self.bookings.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        if booking.user_id != user_id:
            raise ForbiddenError("You cannot cancel this booking")
        self._ensure_cancel_allowed(booking.start_time)
        return await self.bookings.cancel(booking)

    @staticmethod
    def _schedule_reminder(booking: Booking) -> None:
        now = datetime.now()
        reminder_time = booking.start_time - timedelta(days=1)
        if reminder_time <= now:
            return
        send_booking_reminder.apply_async(
            args=[
                booking.user.email,
                booking.user.full_name,
                booking.start_time.isoformat(),
            ],
            eta=reminder_time,
        )

    async def _ensure_table_exists(self, table_id: int) -> None:
        table = await self.tables.get_by_id(table_id)
        if not table:
            raise NotFoundError("Table not found")

    async def _ensure_slot_available(
        self,
        table_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: int | None = None,
    ) -> None:
        has_conflict = await self.bookings.has_conflict(
            table_id, start_time, end_time, exclude_booking_id
        )
        if has_conflict:
            raise BusinessError("Table is not available for the selected time")

    @staticmethod
    def _ensure_within_working_hours(start_time: datetime, end_time: datetime) -> None:
        open_time = time(12, 0)
        close_time = time(22, 0)

        if start_time.time() < open_time or end_time.time() > close_time:
            raise BusinessError("Requested time is outside of working hours")

    @staticmethod
    def _ensure_same_day(start_time: datetime, end_time: datetime) -> None:
        if end_time.date() != start_time.date():
            raise BusinessError("Requested time is outside of working hours")

    @staticmethod
    def _ensure_cancel_allowed(start_time: datetime) -> None:
        now = datetime.now()
        if start_time - now < timedelta(hours=1):
            raise BusinessError(
                "Booking cannot be canceled less than 1 hour before start"
            )

    @staticmethod
    def _normalize_time(target_time: time) -> time:
        if target_time.tzinfo is None:
            return target_time
        return target_time.replace(tzinfo=None)
