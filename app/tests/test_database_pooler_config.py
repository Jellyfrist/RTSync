"""Unit tests for SQLAlchemy connection options used in Vercel."""

import unittest
from unittest.mock import patch

from app.infrastructure.database import Database


class DatabasePoolerConfigTests(unittest.TestCase):
    def test_transaction_pooler_disables_prepared_statements(self):
        uri = "postgresql+psycopg://postgres.project:password@pooler.example.com:6543/postgres"
        with patch("app.infrastructure.database.create_engine") as create_engine, \
             patch("app.infrastructure.database.sessionmaker"):
            Database(uri)
        create_engine.assert_called_once_with(
            uri, pool_pre_ping=True, connect_args={"prepare_threshold": None}
        )

    def test_direct_connection_uses_driver_defaults(self):
        uri = "postgresql+psycopg://postgres:password@db.example.com:5432/postgres"
        with patch("app.infrastructure.database.create_engine") as create_engine, \
             patch("app.infrastructure.database.sessionmaker"):
            Database(uri)
        create_engine.assert_called_once_with(
            uri, pool_pre_ping=True, connect_args={}
        )


if __name__ == "__main__":
    unittest.main()
