from app.models.product import Product
from app.infrastructure.orm import ProductRecord
from app.repositories.base import SqlAlchemyRepository


class CatalogRepository(SqlAlchemyRepository):
    record_type = ProductRecord

    def list(self) -> list[Product]:
        return [Product(row.sku, row.name, row.category, row.stock, row.price, row.unit, row.reorder_point, tuple(row.supplier_ids), row.cost_price, row.sale_price) for row in self.records()]
