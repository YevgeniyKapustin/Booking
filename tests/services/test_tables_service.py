from datetime import datetime

import pytest

from src.core.errors import BusinessError
from src.tables.services import TableService


def test_within_working_hours() -> None:
    start_time = datetime(2026, 2, 7, 12, 0)
    end_time = datetime(2026, 2, 7, 14, 0)
    TableService._ensure_within_working_hours(start_time, end_time)


def test_outside_working_hours_raises() -> None:
    start_time = datetime(2026, 2, 7, 11, 0)
    end_time = datetime(2026, 2, 7, 13, 0)
    with pytest.raises(BusinessError):
        TableService._ensure_within_working_hours(start_time, end_time)


def test_different_day_raises() -> None:
    start_time = datetime(2026, 2, 7, 21, 0)
    end_time = datetime(2026, 2, 8, 1, 0)
    with pytest.raises(BusinessError):
        TableService._ensure_same_day(start_time, end_time)
