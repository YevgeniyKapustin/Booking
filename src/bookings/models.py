from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base
from src.db.types import created_at

if TYPE_CHECKING:
    from src.auth.models import User
    from src.tables.models import Table


class BookingStatus(StrEnum):
    ACTIVE = "active"
    CANCELED = "canceled"


class Booking(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("usr.id"), index=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("table.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[BookingStatus] = mapped_column(
        Enum(
            BookingStatus,
            name="booking_status",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        default=BookingStatus.ACTIVE,
    )
    created_at: Mapped[created_at]

    user: Mapped["User"] = relationship("User", back_populates="bookings")
    table: Mapped["Table"] = relationship("Table", back_populates="bookings")
