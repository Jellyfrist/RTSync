"""Add the optional contact phone field to existing employee records.

This additive migration preserves all existing payroll data. Run it once
against the existing PostgreSQL database before deploying code that reads the
new column.
"""

from sqlalchemy import text

from app.config import settings
from app.infrastructure.database import Database


def migrate(database: Database) -> None:
    if database.engine.dialect.name != "postgresql":
        raise RuntimeError("The employee phone migration requires PostgreSQL.")
    with database.engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE employees "
                "ADD COLUMN IF NOT EXISTS phone VARCHAR(64) NOT NULL DEFAULT ''"
            )
        )


if __name__ == "__main__":
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required in the root .env file.")
    migrate(Database(settings.database_url))
    print("Employee phone column is ready.")
