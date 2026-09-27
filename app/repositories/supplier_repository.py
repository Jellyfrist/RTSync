from app.infrastructure.orm import SupplierRecord
from app.models.supplier import Supplier
from app.repositories.base import SqlAlchemyRepository


class SupplierRepository(SqlAlchemyRepository):
    record_type = SupplierRecord

    def list(self) -> list[Supplier]:
        return [Supplier(row.id, row.name, row.category, row.delivery, row.sku_count) for row in self.records()]
