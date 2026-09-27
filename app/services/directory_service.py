from typing import Generic, TypeVar

from app.repositories.base import ReadRepository

T = TypeVar("T")


class DirectoryService(Generic[T]):
    """Shared read use case for customers, suppliers and employees."""

    def __init__(self, repository: ReadRepository[T]) -> None:
        self.repository = repository

    def list(self) -> list[T]:
        return self.repository.list()
