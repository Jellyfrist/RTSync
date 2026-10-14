"""Prevent regressions that would expose production business data without login."""
import unittest

from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app


class PublicDemoSafetyTest(unittest.TestCase):
    def setUp(self):
        config = Settings(app_env="production", public_demo_mode=True, database_url="")
        self.client = TestClient(create_app(config))

    def test_health_is_public(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_anonymous_business_read_is_blocked(self):
        response = self.client.get("/api/inventory/products")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers.get("cache-control"), "no-store")

    def test_anonymous_business_write_is_blocked(self):
        response = self.client.post("/api/inventory/products", json={})
        self.assertEqual(response.status_code, 503)

    def test_legacy_docs_are_blocked(self):
        self.assertEqual(self.client.get("/docs").status_code, 503)
        self.assertEqual(self.client.get("/openapi.json").status_code, 503)


if __name__ == "__main__":
    unittest.main()
