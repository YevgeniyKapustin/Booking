from datetime import date, datetime, time, timedelta

from src.core.errors import BusinessError, NotFoundError
from src.core.logging_decorators import log_service
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
        start_time = datetime.combine(target_date, target_time)
        end_time = start_time + timedelta(hours=2)

        self._ensure_within_working_hours(start_time, end_time)
        self._ensure_same_day(start_time, end_time)

        return await self.tables.get_available(start_time, end_time, seats)

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
    def _normalize_time(target_time: time) -> time:
        if target_time.tzinfo is None:
            return target_time
        return target_time.replace(tzinfo=None)
