from datetime import date, datetime, time, timedelta

from src.core.config import settings
from src.core.errors import BusinessError, NotFoundError
from src.core.logging_decorators import log_service
from src.core.time_utils import (
    combine_local,
    is_past,
    is_valid_slot_time,
    is_within_horizon,
    normalize_time,
    to_utc,
)
from src.tables.repositories import TableRepository


class TableService:
    def __init__(self, tables: TableRepository) -> None:
        self.tables = tables

    @log_service
    async def get_tables(self):
        return await self.tables.get_all()

    @log_service
    async def get_table(self, table_id: int):
        table = await self.tables.get_by_id(table_id)
        if not table:
            raise NotFoundError("Table not found")
        return table

    @log_service
    async def create_table(self, name: str, seats: int):
        table_id = await self.tables.create(name, seats)
        table = await self.tables.get_by_id(table_id)
        if not table:
            raise NotFoundError("Table not found")
        return table

    @log_service
    async def update_table(
        self,
        table_id: int,
        name: str | None = None,
        seats: int | None = None,
    ):
        table = await self.tables.get_by_id(table_id)
        if not table:
            raise NotFoundError("Table not found")
        return await self.tables.update(table, name, seats)

    @log_service
    async def delete_table(self, table_id: int) -> None:
        table = await self.tables.get_by_id(table_id)
        if not table:
            raise NotFoundError("Table not found")
        await self.tables.delete(table)

    @log_service
    async def list_available_tables(
        self,
        target_date: date,
        target_time: time,
        seats: int | None = None,
    ):
        target_time = self._normalize_time(target_time)
        local_start = combine_local(target_date, target_time)
        local_end = local_start + timedelta(
            minutes=settings.booking_duration_minutes
        )

        self._ensure_within_working_hours(local_start, local_end)
        self._ensure_same_day(local_start, local_end)
        self._ensure_booking_window(local_start)

        start_time = to_utc(local_start)
        end_time = to_utc(local_end)
        return await self.tables.get_available(start_time, end_time, seats)

    @staticmethod
    def _ensure_within_working_hours(start_time: datetime, end_time: datetime) -> None:
        open_time = time.fromisoformat(settings.booking_open_time)
        close_time = time.fromisoformat(settings.booking_close_time)

        if start_time.time() < open_time or end_time.time() > close_time:
            raise BusinessError("Requested time is outside of working hours")

    @staticmethod
    def _ensure_same_day(start_time: datetime, end_time: datetime) -> None:
        if end_time.date() != start_time.date():
            raise BusinessError("Requested time is outside of working hours")

    @staticmethod
    def _normalize_time(target_time: time) -> time:
        return normalize_time(target_time)

    @staticmethod
    def _ensure_booking_window(start_time: datetime) -> None:
        if is_past(start_time):
            raise BusinessError("Booking time cannot be in the past")
        if not is_within_horizon(start_time, settings.booking_max_days_ahead):
            raise BusinessError("Booking date is too far in the future")
        if not is_valid_slot_time(start_time, settings.booking_slot_minutes):
            raise BusinessError("Booking time must align to the slot minutes")
