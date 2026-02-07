import pytest

from src.tasks import tasks as celery_tasks


@pytest.mark.asyncio
async def test_register_returns_token(client, monkeypatch) -> None:
    monkeypatch.setattr(
        celery_tasks.send_welcome_email,
        "delay",
        lambda *args, **kwargs: None,
    )

    response = await client.post(
        "/auth/register",
        json={
            "email": "new-user@example.com",
            "password": "password",
            "full_name": "New User",
            "phone_number": "1234567890",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
