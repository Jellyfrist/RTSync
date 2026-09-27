import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.dependencies import get_database
from app.infrastructure.database import Database
from app.infrastructure.orm import EmployeeRecord
from app.main import create_app


class InventoryModelTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        url = f"sqlite+pysqlite:///{Path(self.temporary.name) / 'inventory.db'}"
        self.database = Database(url)
        self.database.create_tables()
        application = create_app(Settings(_env_file=None, database_url=url))
        application.dependency_overrides[get_database] = lambda: self.database
        self.client = TestClient(application)

    def tearDown(self):
        self.client.close()
        self.database.engine.dispose()
        self.temporary.cleanup()

    def test_one_product_catalog_supplier_links_and_decimal_price(self):
        product = self.client.post('/api/catalog/products', json={
            'sku': 'P-1', 'name': 'Panel', 'category': 'Solar', 'unit': 'แผง',
            'reorder_point': 2, 'price': '12.34',
        })
        self.assertEqual(product.status_code, 201, product.text)
        self.assertEqual(product.json()['price'], '12.34')
        self.assertEqual(product.json()['unit'], 'แผง')
        self.assertEqual(product.json()['supplier_ids'], [])
        supplier = self.client.post('/api/suppliers', json={
            'name': 'Supplier', 'category': 'Solar', 'delivery': '2 days',
        }).json()
        path = f"/api/suppliers/{supplier['id']}/products/P-1"
        self.assertEqual(self.client.post(path).status_code, 200)
        self.assertEqual(self.client.post(path).status_code, 200)
        self.assertEqual(self.client.get('/api/catalog/products').json()[0]['supplier_ids'], [supplier['id']])
        self.assertEqual(self.client.get('/api/suppliers').json()[0]['sku_count'], 1)
        self.assertEqual(Decimal(self.client.get('/api/catalog/products').json()[0]['price']), Decimal('12.34'))

    def test_receipt_and_issue_share_stock_ledger_and_reject_invalid_issue(self):
        self.client.post('/api/catalog/products', json={
            'sku': 'P-1', 'name': 'Panel', 'category': 'Solar', 'price': '9.99',
        })
        supplier = self.client.post('/api/suppliers', json={
            'name': 'Supplier', 'category': 'Solar', 'delivery': '2 days',
        }).json()
        order_response = self.client.post('/api/purchase-orders', json={
            'supplier_id': supplier['id'], 'actor': 'buyer',
            'lines': [{'product_sku': 'P-1', 'quantity': 5}],
        })
        self.assertEqual(order_response.status_code, 201, order_response.text)
        order = order_response.json()
        self.client.post(f"/api/purchase-orders/{order['id']}/approve", json={'actor': 'manager'})
        receipt = self.client.post(f"/api/purchase-orders/{order['id']}/receipts", json={
            'reference': 'GR-1', 'actor': 'buyer',
            'lines': [{'order_line_id': order['lines'][0]['id'], 'quantity': 5}],
        })
        self.assertEqual(receipt.status_code, 201, receipt.text)
        issue_body = {'reference': 'SALE-1', 'actor': 'seller', 'lines': [{'product_sku': 'P-1', 'quantity': 3}]}
        issue = self.client.post('/api/catalog/stock-issues', json=issue_body)
        self.assertEqual(issue.status_code, 201, issue.text)
        self.assertEqual(self.client.get('/api/catalog/products').json()[0]['stock'], 2)
        movements = self.client.get('/api/catalog/stock-movements').json()
        self.assertEqual({item['movement_type'] for item in movements}, {'receipt', 'issue'})
        self.assertEqual(sorted(item['quantity_change'] for item in movements), [-3, 5])
        self.assertEqual(self.client.post('/api/catalog/stock-issues', json=issue_body).status_code, 409)
        over = self.client.post('/api/catalog/stock-issues', json={
            'reference': 'SALE-2', 'actor': 'seller', 'lines': [{'product_sku': 'P-1', 'quantity': 3}],
        })
        self.assertEqual(over.status_code, 409, over.text)
        self.assertEqual(self.client.get('/api/catalog/products').json()[0]['stock'], 2)
        self.assertEqual(len(self.client.get('/api/catalog/stock-movements').json()), 2)

    def test_multi_line_issue_is_all_or_nothing(self):
        for sku in ('P-1', 'P-2'):
            self.client.post('/api/catalog/products', json={
                'sku': sku, 'name': sku, 'category': 'Solar', 'price': '1.00',
            })
        failed = self.client.post('/api/catalog/stock-issues', json={
            'reference': 'SALE-1', 'actor': 'seller', 'lines': [
                {'product_sku': 'P-1', 'quantity': 1},
                {'product_sku': 'P-2', 'quantity': 1},
            ],
        })
        self.assertEqual(failed.status_code, 409, failed.text)
        self.assertEqual(len(self.client.get('/api/catalog/stock-movements').json()), 0)
        self.assertTrue(all(row['stock'] == 0 for row in self.client.get('/api/catalog/products').json()))

    def test_employee_salary_is_decimal(self):
        with self.database.session_factory.begin() as session:
            session.add(EmployeeRecord(id='E-1', name='Worker', role='Engineer',
                                       salary=Decimal('25000.25'), overtime_hours=1.5))
        employee = self.client.get('/api/employees')
        self.assertEqual(employee.status_code, 200, employee.text)
        self.assertEqual(employee.json()[0]['salary'], '25000.25')


if __name__ == '__main__':
    unittest.main()
