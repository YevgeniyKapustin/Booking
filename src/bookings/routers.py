from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.bookings.repositories import BookingRepository
from src.bookings.schemas import BookingCreate, BookingRead, BookingUpdate
from src.bookings.services import BookingService
from src.core.logging_decorators import log_endpoint
from src.db.session import get_session
from src.tables.repositories import TableRepository

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post(
    "/",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a booking",
    description=("Creates a 2-hour booking slot for the selected table and time."),
)
@log_endpoint
async def create_booking(
    payload: BookingCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> BookingRead:
    service = BookingService(BookingRepository(session), TableRepository(session))
    booking = await service.create_booking(
        current_user.id, payload.table_id, payload.date, payload.time
    )
    return BookingRead.model_validate(booking)


@router.get(
    "/my",
    response_model=list[BookingRead],
    summary="Get my bookings",
    description="Returns upcoming active bookings for the current user.",
)
@log_endpoint
async def list_my_bookings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[BookingRead]:
    service = BookingService(BookingRepository(session), TableRepository(session))
    bookings = await service.list_my_bookings(current_user.id)
    return [BookingRead.model_validate(booking) for booking in bookings]


@router.patch(
    "/{booking_id}",
    response_model=BookingRead,
    summary="Update booking time",
    description="Reschedules a booking to a new date/time if the slot is free.",
)
@log_endpoint
async def update_booking_time(
    booking_id: int,
    payload: BookingUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> BookingRead:
    service = BookingService(BookingRepository(session), TableRepository(session))
    booking = await service.update_booking_time(
        booking_id, current_user.id, payload.date, payload.time
    )
    return BookingRead.model_validate(booking)


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel a booking",
    description="Cancels an active booking (not allowed within 1 hour of start).",
)
@log_endpoint
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    service = BookingService(BookingRepository(session), TableRepository(session))
    await service.cancel_booking(booking_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
