from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from src.db.types import type_annotation_map


class Base(DeclarativeBase):
    type_annotation_map = type_annotation_map

    id: Mapped[int] = mapped_column(primary_key=True)

    @declared_attr.directive
    def __tablename__(self) -> str:
        return self.__name__.lower()
