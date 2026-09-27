from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.orm import (
    ProductRecord, PurchaseOrderEventRecord, PurchaseOrderLineRecord,
    PurchaseOrderRecord, PurchaseReceiptRecord, StockMovementRecord,
    SupplierRecord,
    SupplierProductRecord,
)


class PurchaseOrderRepository:
    """Database access used by the procurement workflow."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def transaction(self):
        return self.session.begin()

    def add(self, record) -> None:
        self.session.add(record)

    def flush(self) -> None:
        self.session.flush()

    def supplier(self, supplier_id: str) -> SupplierRecord | None:
        return self.session.get(SupplierRecord, supplier_id)

    def link_supplier_product(self, supplier: SupplierRecord, sku: str) -> None:
        if self.session.get(SupplierProductRecord, (supplier.id, sku)) is None:
            self.session.add(SupplierProductRecord(supplier_id=supplier.id, product_sku=sku))
            supplier.sku_count += 1

    def product(self, sku: str, *, lock: bool = False) -> ProductRecord | None:
        statement = select(ProductRecord).where(ProductRecord.sku == sku)
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

    def order(self, order_id: str, *, lock: bool = False) -> PurchaseOrderRecord | None:
        statement = select(PurchaseOrderRecord).where(PurchaseOrderRecord.id == order_id)
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

    def lines(self, order_id: str, *, lock: bool = False) -> list[PurchaseOrderLineRecord]:
        statement = select(PurchaseOrderLineRecord).where(PurchaseOrderLineRecord.order_id == order_id).order_by(PurchaseOrderLineRecord.id)
        if lock:
            statement = statement.with_for_update()
        return list(self.session.scalars(statement))

    def orders(self) -> list[PurchaseOrderRecord]:
        return list(self.session.scalars(select(PurchaseOrderRecord).order_by(PurchaseOrderRecord.created_at.desc())))

    def receipt_reference_exists(self, order_id: str, reference: str) -> bool:
        statement = select(PurchaseReceiptRecord.id).where(
            PurchaseReceiptRecord.order_id == order_id,
            PurchaseReceiptRecord.reference == reference,
        )
        return self.session.scalar(statement) is not None

    def receipts(self, order_id: str) -> list[PurchaseReceiptRecord]:
        statement = select(PurchaseReceiptRecord).where(PurchaseReceiptRecord.order_id == order_id).order_by(PurchaseReceiptRecord.received_at)
        return list(self.session.scalars(statement))

    def events(self, order_id: str) -> list[PurchaseOrderEventRecord]:
        statement = select(PurchaseOrderEventRecord).where(PurchaseOrderEventRecord.order_id == order_id).order_by(PurchaseOrderEventRecord.created_at)
        return list(self.session.scalars(statement))

    def movements(self, sku: str | None = None) -> list[StockMovementRecord]:
        statement = select(StockMovementRecord).order_by(StockMovementRecord.created_at.desc())
        if sku is not None:
            statement = statement.where(StockMovementRecord.product_sku == sku)
        return list(self.session.scalars(statement))
