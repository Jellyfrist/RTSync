"""Regression tests for Store owner/Staff access based on Chapter 10.

Does not require database records or modify the use case document.
"""
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.authorization import can_access_api, can_access_page, role_for_email
from app.config import Settings
from app.main import create_app


class ActorMatrixTests(unittest.TestCase):
    def test_owner_has_all_eight_existing_pages(self):
        for page in (
            "/payroll", "/suppliers", "/inventory", "/customers",
            "/sales", "/installations", "/service", "/fuel-claims",
        ):
            with self.subTest(page=page):
                self.assertTrue(can_access_page("owner", page))

    def test_employee_has_six_daily_work_pages(self):
        for page in (
            "/inventory", "/customers", "/sales",
            "/installations", "/service", "/fuel-claims",
        ):
            with self.subTest(page=page):
                self.assertTrue(can_access_page("employee", page))
        self.assertFalse(can_access_page("employee", "/payroll"))
        self.assertFalse(can_access_page("employee", "/suppliers"))

    def test_reject_unknown_actors(self):
        self.assertFalse(can_access_page("guest", "/customers"))
        self.assertFalse(can_access_api("guest", "GET", "/api/customers"))

    def test_case_insensitive_owner_and_employee_assignments(self):
        self.assertEqual(
            role_for_email(" OWNER@EXAMPLE.com ", "owner@example.com", "employee@example.com"),
            "owner",
        )
        self.assertEqual(
            role_for_email("employee@example.com", "owner@example.com", "employee@example.com"),
            "employee",
        )
        self.assertIsNone(role_for_email("unknown@example.com", "owner@example.com", "employee@example.com"))

    def test_owner_only_payroll_and_procurement_api(self):
        for method, path in (
            ("GET", "/api/employees"), ("POST", "/api/employees"),
            ("GET", "/api/operations/purchaseOrders"),
            ("PATCH", "/api/operations/purchaseOrders/PO-123"),
            ("GET", "/api/purchase-orders"),
            ("POST", "/api/suppliers/categories"),
            ("PATCH", "/api/suppliers/SUP-1"),
            ("GET", "/api/catalog/stock-movements"),
        ):
            with self.subTest(method=method, path=path):
                self.assertTrue(can_access_api("owner", method, path))
                self.assertFalse(can_access_api("employee", method, path))

    def test_staff_allowed_existing_inventory_flow(self):
        for method, path in (
            ("GET", "/api/inventory/products"),
            ("POST", "/api/inventory/products"),
            ("PUT", "/api/inventory/products/SKU-1"),
            ("POST", "/api/inventory/products/SKU-1/receive"),
            ("GET", "/api/inventory/categories"),
            ("POST", "/api/inventory/categories"),
            ("GET", "/api/suppliers"),
            ("GET", "/api/suppliers/categories"),
            ("POST", "/api/suppliers"),
            ("POST", "/api/suppliers/SUP-1/products/SKU-1"),
            ("DELETE", "/api/suppliers/SUP-1/products/SKU-1"),
            ("POST", "/api/operations/purchaseOrders"),
        ):
            with self.subTest(method=method, path=path):
                self.assertTrue(can_access_api("employee", method, path))

    def test_staff_allowed_existing_customer_sales_service_and_fuel_usecases(self):
        for method, path in (
            ("GET", "/api/customers"), ("POST", "/api/customers"),
            ("PATCH", "/api/customers/CUST-1"),
            ("GET", "/api/catalog/products"),
            ("GET", "/api/operations/quotations"),
            ("POST", "/api/operations/quotations"),
            ("POST", "/api/operations/sales"),
            ("PATCH", "/api/operations/sales/SO-1"),
            ("GET", "/api/operations/appointments"),
            ("POST", "/api/operations/serviceTickets"),
            ("PATCH", "/api/operations/serviceTickets/ST-1"),
            ("GET", "/api/operations/fuelClaims"),
            ("POST", "/api/operations/fuelClaims"),
            ("PATCH", "/api/operations/fuelClaims/FUEL-1"),
        ):
            with self.subTest(method=method, path=path):
                self.assertTrue(can_access_api("employee", method, path))

    def test_unknown_operations_collections_fail_closed(self):
        for method, path in (
            ("GET", "/api/operations/payroll"),
            ("POST", "/api/operations/payroll"),
            ("GET", "/api/operations/other"),
            ("PATCH", "/api/operations/purchaseOrders/PO-1"),
            ("DELETE", "/api/operations/sales/SO-1"),
        ):
            with self.subTest(method=method, path=path):
                self.assertFalse(can_access_api("employee", method, path))


class FastApiGuardTests(unittest.TestCase):
    def setUp(self):
        config = Settings(
            rtsync_auth_required=True, app_env="production",
            database_url="", rtsync_owner_emails="owner@example.com",
            rtsync_employee_emails="staff@example.com",
        )
        self.client = TestClient(create_app(config))

    def test_employee_cannot_read_payroll(self):
        staff = {"role": "employee", "email": "staff@example.com"}
        with patch("app.main.authorized_user", new_callable=AsyncMock, return_value=staff):
            response = self.client.get("/api/employees")
        self.assertEqual(response.status_code, 403)

    def test_employee_cannot_read_owner_purchase_orders(self):
        staff = {"role": "employee", "email": "staff@example.com"}
        with patch("app.main.authorized_user", new_callable=AsyncMock, return_value=staff):
            response = self.client.get("/api/operations/purchaseOrders")
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_business_api_returns_401(self):
        with patch("app.main.authorized_user", new_callable=AsyncMock) as mock:
            from fastapi import HTTPException
            mock.side_effect = HTTPException(status_code=401, detail="Authentication required")
            response = self.client.post("/api/operations/fuelClaims", json={})
        self.assertEqual(response.status_code, 401)

    def test_health_requires_no_login(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)


if __name__ == "__main__":
    unittest.main()
