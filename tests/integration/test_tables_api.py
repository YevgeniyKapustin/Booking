import pytest

from tests.integration.helpers import auth_header, create_user


@pytest.mark.asyncio
async def test_admin_can_create_table(client, db_session) -> None:
    admin = await create_user(db_session, is_admin=True)

    response = await client.post(
        "/tables/",
        json={"name": "VIP", "seats": 4},
        headers=auth_header(admin.id),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "VIP"
    assert data["seats"] == 4


@pytest.mark.asyncio
async def test_user_cannot_list_tables(client, db_session) -> None:
    user = await create_user(db_session, is_admin=False)

    response = await client.get("/tables/", headers=auth_header(user.id))
    assert response.status_code == 403
