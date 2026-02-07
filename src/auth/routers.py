from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories import UserRepository
from src.auth.schemas import Token, UserCreate, UserLogin
from src.auth.services import AuthService
from src.core.logging_decorators import log_endpoint
from src.db.session import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=Token,
    summary="Register a new user",
    description="Creates a user account and returns a bearer access token.",
)
@log_endpoint
async def register(
    payload: UserCreate, session: AsyncSession = Depends(get_session)
) -> Token:
    service = AuthService(UserRepository(session))
    return await service.register(payload)


@router.post(
    "/login",
    response_model=Token,
    summary="Log in and get a token",
    description="Validates user credentials and returns a bearer access token.",
)
@log_endpoint
async def login(
    payload: UserLogin, session: AsyncSession = Depends(get_session)
) -> Token:
    service = AuthService(UserRepository(session))
    return await service.login(payload)
