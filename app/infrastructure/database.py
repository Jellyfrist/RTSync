from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for PostgreSQL ORM tables."""


class Database:
    """Create SQLAlchemy engines and sessions from application settings."""

    def __init__(self, url: str) -> None:
        self.engine = create_engine(url, pool_pre_ping=True)
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)

    def session(self) -> Generator[Session, None, None]:
        session = self.session_factory()
        try:
            yield session
        finally:
            session.close()

    def create_tables(self) -> None:
        from app.infrastructure.orm import BaseModel

        BaseModel.metadata.create_all(self.engine)
