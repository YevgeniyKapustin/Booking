import asyncio
import os
import sys
from pathlib import Path

from sqlalchemy import select

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

if os.environ.get("POSTGRES_HOST") == "db" and not Path("/.dockerenv").exists():
    os.environ["POSTGRES_HOST"] = "localhost"

from src.auth.models import User
from src.bookings.models import Booking
from src.db.session import SessionFactory
from src.tables.models import Table

TABLE_CONFIG = {
    2: 7,
    3: 6,
    6: 3,
}


async def seed_tables() -> None:
    async with SessionFactory() as session:
        existing = await session.execute(select(Table.id))
        if existing.first() is not None:
            print("Tables already exist, skipping.")
            return

        tables: list[Table] = []
        for seats, count in TABLE_CONFIG.items():
            for index in range(1, count + 1):
                tables.append(Table(name=f"T{seats}-{index}", seats=seats))

        session.add_all(tables)
        await session.commit()
        print(f"Inserted {len(tables)} tables.")


if __name__ == "__main__":
    asyncio.run(seed_tables())
