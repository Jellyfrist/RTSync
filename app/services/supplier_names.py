import unicodedata

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.infrastructure.orm import SupplierRecord


def normalize_supplier_name(name: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", name).split()).casefold()


def find_supplier_name_conflict(
    session: Session,
    name: str,
    *,
    exclude_id: str | None = None,
) -> SupplierRecord | None:
    normalized_name = normalize_supplier_name(name)
    if not normalized_name:
        return None

    if session.get_bind().dialect.name == "postgresql":
        session.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:supplier_name))"),
            {"supplier_name": f"supplier-name:{normalized_name}"},
        )

    records = session.scalars(select(SupplierRecord).order_by(SupplierRecord.id))
    return next(
        (
            record
            for record in records
            if record.id != exclude_id
            and normalize_supplier_name(record.name) == normalized_name
        ),
        None,
    )
