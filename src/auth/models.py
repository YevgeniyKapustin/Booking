from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base
from src.db.types import created_at, str_32, str_256

if TYPE_CHECKING:
    from src.bookings.models import Booking


class User(Base):
    __tablename__ = "usr"
    email: Mapped[str_256] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    full_name: Mapped[str]
    phone_number: Mapped[str_32]
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
    )
