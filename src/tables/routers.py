from datetime import date as date_type
from datetime import time as time_type

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_admin, get_current_user
from src.auth.models import User
from src.core.logging_decorators import log_endpoint
from src.db.session import get_session
from src.tables.repositories import TableRepository
from src.tables.schemas import TableCreate, TableRead, TableUpdate
from src.tables.services import TableService

router = APIRouter(prefix="/tables", tags=["tables"])


@router.get(
    "/available",
    response_model=list[TableRead],
    summary="Get available tables",
    description=(
        "Returns tables available for a 2-hour slot at the requested date/time."
    ),
)
@log_endpoint
async def list_available_tables(
    date: date_type = Query(
        ...,
        description="Booking date in YYYY-MM-DD format.",
        examples=["2026-02-07"],
    ),
    time: time_type = Query(
        ...,
        description="Booking start time in HH:MM (24-hour) format.",
        examples=["19:30"],
    ),
    seats: int | None = Query(
        default=None,
        description="Minimum number of seats required.",
        examples=[2],
    ),
    _current_user: object = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[TableRead]:
    service = TableService(TableRepository(session))
    return await service.list_available_tables(date, time, seats)


@router.post(
    "/",
    response_model=TableRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create table (admin)",
    description="Creates a new table. Admin access required.",
)
@log_endpoint
async def create_table(
    payload: TableCreate,
    _current_admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
) -> TableRead:
    service = TableService(TableRepository(session))
    table = await service.create_table(payload.name, payload.seats)
    return TableRead.model_validate(table)


@router.get(
    "/",
    response_model=list[TableRead],
    summary="Get tables (admin)",
    description="Returns all tables. Admin access required.",
)
@log_endpoint
async def get_tables(
    _current_admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
) -> list[TableRead]:
    service = TableService(TableRepository(session))
    tables = await service.get_tables()
    return [TableRead.model_validate(table) for table in tables]


@router.get(
    "/{table_id}",
    response_model=TableRead,
    summary="Get table (admin)",
    description="Returns table details by id. Admin access required.",
)
@log_endpoint
async def get_table(
    table_id: int,
    _current_admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
) -> TableRead:
    service = TableService(TableRepository(session))
    table = await service.get_table(table_id)
    return TableRead.model_validate(table)


@router.patch(
    "/{table_id}",
    response_model=TableRead,
    summary="Update table (admin)",
    description="Updates table name or seat count. Admin access required.",
)
@log_endpoint
async def update_table(
    table_id: int,
    payload: TableUpdate,
    _current_admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
) -> TableRead:
    service = TableService(TableRepository(session))
    table = await service.update_table(table_id, payload.name, payload.seats)
    return TableRead.model_validate(table)


@router.delete(
    "/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete table (admin)",
    description="Deletes a table by id. Admin access required.",
)
@log_endpoint
async def delete_table(
    table_id: int,
    _current_admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
) -> Response:
    service = TableService(TableRepository(session))
    await service.delete_table(table_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
