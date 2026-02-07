from typing import Any, cast

import pytest

from src.auth.services import AuthService
from src.core.errors import BusinessError


class FakeUserRepository:
    def __init__(self, exists: bool) -> None:
        self._exists = exists

    async def get_by_email(self, email: str):
        if self._exists:
            return object()
        return None


@pytest.mark.asyncio
async def test_validate_email_raises_for_existing_user() -> None:
    service = AuthService(cast(Any, FakeUserRepository(exists=True)))
    with pytest.raises(BusinessError):
        await service.validate_email("user@example.com")


@pytest.mark.asyncio
async def test_validate_email_allows_new_user() -> None:
    service = AuthService(cast(Any, FakeUserRepository(exists=False)))
    await service.validate_email("user@example.com")
