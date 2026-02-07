from datetime import datetime, timezone
from typing import Annotated

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import mapped_column

str_256 = Annotated[str, 256]
str_64 = Annotated[str, 64]
str_32 = Annotated[str, 32]
created_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    ),
]

type_annotation_map = {
    str_256: String(256),
    str_64: String(64),
    str_32: String(32),
}
