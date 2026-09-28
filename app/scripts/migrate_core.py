"""Apply the inventory model upgrade to an existing PostgreSQL database."""

from sqlalchemy import inspect, text

from app.config import settings
from app.infrastructure.database import Database
from app.infrastructure.orm import BaseModel


def migrate(database: Database) -> None:
    if database.engine.dialect.name != "postgresql":
        raise RuntimeError("The existing-database migration requires PostgreSQL.")
    with database.engine.begin() as connection:
        BaseModel.metadata.create_all(connection)
        connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS unit VARCHAR(32) NOT NULL DEFAULT 'ชิ้น'"))
        connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS reorder_point INTEGER NOT NULL DEFAULT 0"))
        connection.execute(text("ALTER TABLE products ALTER COLUMN price TYPE NUMERIC(14, 2) USING round(price::numeric, 2)"))
        connection.execute(text("ALTER TABLE employees ALTER COLUMN salary TYPE NUMERIC(14, 2) USING round(salary::numeric, 2)"))
        connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS cost_price NUMERIC(14, 2)"))
        connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS sale_price NUMERIC(14, 2)"))
        connection.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS email VARCHAR(255) NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS tax_id VARCHAR(64) NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS contact_name VARCHAR(255) NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS address JSONB NOT NULL DEFAULT '{}'::jsonb"))
        connection.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS system VARCHAR(255) NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS description VARCHAR(500) NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS contact_name VARCHAR(255) NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS contact_phone VARCHAR(64) NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS contact_email VARCHAR(255) NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS payment_terms VARCHAR(120) NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS email VARCHAR(255) NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS start_date DATE"))
        connection.execute(text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS overtime_rate NUMERIC(14, 2) NOT NULL DEFAULT 0"))
        connection.execute(text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS allowance NUMERIC(14, 2) NOT NULL DEFAULT 0"))
        connection.execute(text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS deduction NUMERIC(14, 2) NOT NULL DEFAULT 0"))
        connection.execute(text("ALTER TABLE stock_movements ALTER COLUMN receipt_line_id DROP NOT NULL"))
        columns = {column["name"] for column in inspect(connection).get_columns("stock_movements")}
        if "issue_line_id" not in columns:
            connection.execute(text("ALTER TABLE stock_movements ADD COLUMN issue_line_id VARCHAR(36) UNIQUE REFERENCES stock_issue_lines(id)"))
        checks = {constraint["name"] for constraint in inspect(connection).get_check_constraints("stock_movements")}
        if "ck_stock_movement_source" not in checks:
            connection.execute(text("ALTER TABLE stock_movements ADD CONSTRAINT ck_stock_movement_source CHECK ((receipt_line_id IS NOT NULL) <> (issue_line_id IS NOT NULL))"))
        product_checks = {constraint["name"] for constraint in inspect(connection).get_check_constraints("products")}
        if "ck_product_stock_nonnegative" not in product_checks:
            connection.execute(text("ALTER TABLE products ADD CONSTRAINT ck_product_stock_nonnegative CHECK (stock >= 0)"))
        connection.execute(text("""
            INSERT INTO supplier_products (supplier_id, product_sku)
            SELECT DISTINCT po.supplier_id, line.product_sku
            FROM purchase_orders AS po JOIN purchase_order_lines AS line ON line.order_id = po.id
            ON CONFLICT DO NOTHING
        """))
        connection.execute(text("""
            UPDATE suppliers SET sku_count = (
                SELECT COUNT(*) FROM supplier_products WHERE supplier_id = suppliers.id
            )
        """))


if __name__ == "__main__":
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required in the root .env file.")
    migrate(Database(settings.database_url))
    print("Inventory tables and columns are ready.")
