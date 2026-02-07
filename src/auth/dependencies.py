from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.repositories import UserRepository
from src.core.errors import ForbiddenError, UnauthorizedError
from src.core.security import decode_access_token
from src.db.session import get_session

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        raise UnauthorizedError("Invalid authentication credentials")
    user = await UserRepository(session).get_by_id(payload.sub)
    if not user:
        raise UnauthorizedError("User not found")
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise ForbiddenError("Admin access required")
    return current_user
