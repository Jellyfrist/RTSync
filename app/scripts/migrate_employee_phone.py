"""Add the optional contact phone field to existing employee records.

This additive migration preserves all existing payroll data. It can be run
manually before deployment or lazily on the first employee API request.
"""

from sqlalchemy import text

from app.config import settings
from app.infrastructure.database import Database


def migrate(database: Database) -> None:
    if database.engine.dialect.name != "postgresql":
        raise RuntimeError("The employee phone migration requires PostgreSQL.")
    with database.engine.begin() as connection:
        column_exists = connection.scalar(
            text(
                "SELECT EXISTS ("
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_schema = current_schema() "
                "AND table_name = 'employees' AND column_name = 'phone'"
                ")"
            )
        )
        if not column_exists:
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
