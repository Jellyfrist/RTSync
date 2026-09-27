"""Create the SQLAlchemy tables in the configured Supabase database."""
from app.config import settings
from app.infrastructure.database import Database
from app.scripts.migrate_core import migrate


if __name__ == "__main__":
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required. Copy .env.example to .env and set the Supabase connection string.")
    migrate(Database(settings.database_url))
    print("Database tables are ready.")
