# RT Sync Backend

FastAPI JSON API with MVC controllers, immutable domain models, injectable services and PostgreSQL repositories for Supabase. See the [architecture guide](../docs/architecture.md).

## Run locally

Python 3.10 or newer:

Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
cp -n .env.example .env
# Set DATABASE_URL in .env to your PostgreSQL connection string.
# Set VITE_API_BASE_URL in .env to the backend URL ending in /api.
python -m app.scripts.init_db
uvicorn app.main:app --reload --port 8001
```

API documentation: `http://127.0.0.1:8001/docs`.

## Routes

- `GET /api/health`
- `GET /api/catalog/summary`
- `GET /api/catalog/products` and `POST /api/catalog/products`
- `GET /api/catalog/stock-movements`
- `POST /api/catalog/stock-issues`
- `GET /api/customers`
- `GET /api/suppliers` and `POST /api/suppliers`
- `POST /api/suppliers/{id}/products/{sku}`
- `GET /api/purchase-orders` and `POST /api/purchase-orders`
- `GET /api/purchase-orders/{id}`
- `POST /api/purchase-orders/{id}/approve`
- `POST /api/purchase-orders/{id}/receipts`
- `GET /api/purchase-orders/{id}/history`
- `GET /api/employees`

The API reads and writes PostgreSQL. Set `DATABASE_URL` in the root `.env` to your Supabase connection string. Use the `postgresql+psycopg://` scheme. Start with an empty database, create a supplier and product, then create a draft purchase order, approve it and record one or more receipts. Receipts update stock, received quantities, stock movements and history in one transaction. A duplicate receipt reference for the same order is rejected.

The procurement, inventory and outbound stock issue screens use the API. Customer and payroll screens still use demo fixtures. An outbound issue records a reference and deducts stock atomically; it does not create a sales order or installation schedule. Set `VITE_API_BASE_URL` in the root `.env` to the URL of the backend you run, including `/api`. The example uses port 8001 because port 8000 may already be occupied. Only variables prefixed with `VITE_` are exposed to frontend code; never put database credentials under that prefix. The actor field is currently entered by the user; it records an audit label but does not verify identity. Add authentication and authorization before using approval history as trusted evidence.

`init_db` creates missing tables and applies the inventory upgrade to existing PostgreSQL tables. It adds product units and reorder points, supplier-product links, outbound stock issue tables, and changes price and salary columns to `NUMERIC(14,2)`. Back up existing data before running it on a shared database. It does not cover future schema changes; use versioned migrations for those.

For an existing database, run `python -m app.scripts.migrate_employee_phone` once before deploying the employee phone-field change. This migration only adds `employees.phone` with an empty-string default and preserves existing payroll records.

## Tests

```bash
python -m unittest discover -s app/tests -v
```

`create_app()` creates isolated applications. Override repository providers using `app.dependency_overrides` for tests. SQLAlchemy table mappings are in `app/infrastructure/orm.py`; use a migration tool such as Alembic before production schema changes.
