from datetime import date, datetime
from datetime import time as time_type
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.bookings.models import BookingStatus


class BookingCreate(BaseModel):
    table_id: Annotated[int, Field(examples=[1])]
    date: Annotated[date, Field(examples=["2026-02-07"])]
    time: Annotated[time_type, Field(examples=["19:30"])]


class BookingUpdate(BaseModel):
    date: Annotated[date, Field(examples=["2026-02-07"])]
    time: Annotated[time_type, Field(examples=["20:00"])]


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    table_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
