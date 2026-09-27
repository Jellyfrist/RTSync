from typing import Protocol, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

T = TypeVar("T")


class ReadRepository(Protocol[T]):
    """Storage contract consumed by application services."""

    def list(self) -> list[T]: ...


class SqlAlchemyRepository:
    """Shared read implementation for SQLAlchemy record mappings."""

    record_type: type

    def __init__(self, session: Session) -> None:
        self.session = session

    def records(self) -> list:
        statement: Select = select(self.record_type)
        return list(self.session.scalars(statement))
