from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.db.base import Base
from src.db.types import str_64

if TYPE_CHECKING:
    from src.bookings.models import Booking


class Table(Base):
    name: Mapped[str_64]
    seats: Mapped[int]

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="table",
        cascade="all, delete-orphan",
    )
