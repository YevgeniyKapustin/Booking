from datetime import date, timedelta

import pytest

from src.tasks import tasks as celery_tasks
from tests.integration.helpers import auth_header, create_table, create_user


@pytest.mark.asyncio
async def test_create_booking(client, db_session, monkeypatch) -> None:
    monkeypatch.setattr(
        celery_tasks.send_booking_reminder,
        "apply_async",
        lambda *args, **kwargs: None,
    )

    user = await create_user(db_session)
    table = await create_table(db_session, name="T-1", seats=2)

    payload = {
        "table_id": table.id,
        "date": (date.today() + timedelta(days=2)).isoformat(),
        "time": "19:00",
    }

    response = await client.post(
        "/bookings/",
        json=payload,
        headers=auth_header(user.id),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["table_id"] == table.id
    assert data["user_id"] == user.id
