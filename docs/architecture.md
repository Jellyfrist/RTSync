# RT Sync architecture

The FastAPI backend keeps SQLAlchemy records in `app/infrastructure/orm.py`, API inputs and outputs in `app/schemas`, and workflow rules in `app/services`. The Vue frontend calls the same product API from its inventory, procurement, and outbound issue screens.

## Current data model

| Area | Stored data | Relationship |
| --- | --- | --- |
| Product catalog | `products`: SKU, name, category, unit, reorder point, stock, sale price | One SKU is shared across inventory, purchase orders, and outbound issues. |
| Sourcing | `suppliers`, `supplier_products` | Products and suppliers have a many-to-many relationship. Creating a purchase order also records the association. |
| Purchasing | `purchase_orders`, `purchase_order_lines`, `purchase_receipts`, `purchase_receipt_lines`, `purchase_order_events` | Receipts update stock and append positive ledger entries in one transaction. |
| Outbound stock | `stock_issues`, `stock_issue_lines` | An issue has a unique external reference and deducts stock with negative ledger entries in one transaction. Insufficient stock rejects the entire issue. |
| Ledger | `stock_movements` | Each movement points to either a receipt line or an issue line. The sign of `quantity_change` shows direction. |
| Other directories | `customers`, `employees` | Read-only API directories; the customer and payroll frontend screens still use demo data. |

Prices and salaries use `NUMERIC(14,2)` in PostgreSQL and `Decimal` in Python. API money values are serialized as decimal strings. The quote UI uses integer cents to total displayed prices. The stock value shown in inventory uses **sale price × stock**; it is not cost valuation.

An outbound issue is a stock transaction tied to a sale reference. It is not a persisted sales order and does not schedule installation. Customer sites, installed systems, service logs, warranties, payroll periods, and sales orders remain outside the current data model.

## Database setup

From the repository root, configure `DATABASE_URL` in `.env` and run `python -m app.scripts.init_db`. The command creates all tables on an empty PostgreSQL database. On an existing database it adds the current inventory columns and tables, converts product prices and employee salaries to `NUMERIC(14,2)`, and derives supplier-product links from existing purchase orders. Back up a shared database before applying the upgrade.
