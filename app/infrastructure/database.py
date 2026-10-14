from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for PostgreSQL ORM tables."""


class Database:
    """Create SQLAlchemy engines and sessions from application settings."""

    def __init__(self, url: str) -> None:
        # Supabase's transaction pooler (port 6543) does not support
        # server-side prepared statements; psycopg3 enables them by default.
        # Disable preparation only for that connection mode.
        parsed_url = make_url(url)
        uses_transaction_pooler = parsed_url.drivername == "postgresql+psycopg" and parsed_url.port == 6543
        connect_args = {"prepare_threshold": None} if uses_transaction_pooler else {}
        self.engine = create_engine(url, pool_pre_ping=True, connect_args=connect_args)
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
