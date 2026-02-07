import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.auth import models as _auth_models  # noqa: F401,E402
from src.bookings import models as _booking_models  # noqa: F401,E402
from src.db.base import Base  # noqa: E402
from src.tables import models as _table_models  # noqa: F401,E402


def _format_column(column) -> str:
    column_type = str(column.type)
    pk = " PK" if column.primary_key else ""
    return f"  {column.name} {column_type}{pk}"


def _collect_relationships(metadata) -> list[str]:
    relations: list[str] = []
    for table in metadata.sorted_tables:
        for fk in table.foreign_keys:
            parent = fk.column.table.name
            child = table.name
            label = fk.parent.name
            relations.append(f"  {parent} ||--o{{ {child} : {label}")
    return sorted(set(relations))


def generate_mermaid(output_path: Path) -> None:
    metadata = Base.metadata

    lines: list[str] = ["erDiagram"]
    for table in metadata.sorted_tables:
        lines.append(f"  {table.name} {{")
        for column in table.columns:
            lines.append(_format_column(column))
        lines.append("  }")

    lines.extend(_collect_relationships(metadata))
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    out_dir = project_root / "docs"
    out_dir.mkdir(exist_ok=True)
    generate_mermaid(out_dir / "er.mmd")
    print("ER diagram saved to docs/er.mmd")
