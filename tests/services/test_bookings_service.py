import asyncio
from datetime import datetime, time, timedelta, timezone
from typing import Any, cast

import pytest

from src.bookings.services import BookingService
from src.core.errors import BusinessError


class FakeBookingRepository:
    def __init__(self, conflict: bool) -> None:
        self._conflict = conflict

    async def has_conflict(self, *args, **kwargs) -> bool:
        return self._conflict


class FakeTableRepository:
    async def get_by_id(self, table_id: int):
        return None


def test_normalize_time_removes_tzinfo() -> None:
    aware = time(12, 0, tzinfo=timezone.utc)
    normalized = BookingService._normalize_time(aware)
    assert normalized.tzinfo is None


def test_cancel_too_close_raises() -> None:
    start_time = datetime.now(timezone.utc) + timedelta(minutes=30)
    with pytest.raises(BusinessError):
        BookingService._ensure_cancel_allowed(start_time)


def test_slot_conflict_raises() -> None:
    service = BookingService(
        cast(Any, FakeBookingRepository(conflict=True)),
        cast(Any, FakeTableRepository()),
    )
    start_time = datetime(2026, 2, 7, 12, 0, tzinfo=timezone.utc)
    end_time = datetime(2026, 2, 7, 14, 0, tzinfo=timezone.utc)
    with pytest.raises(BusinessError):
        asyncio.run(service._ensure_slot_available(1, start_time, end_time))
