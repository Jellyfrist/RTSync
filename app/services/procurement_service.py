from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from app.infrastructure.orm import (
    PurchaseOrderEventRecord, PurchaseOrderLineRecord, PurchaseOrderRecord,
    PurchaseReceiptLineRecord, PurchaseReceiptRecord, StockMovementRecord,
)
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.schemas.procurement import CreateOrderInput, ReceiveOrderInput


class WorkflowError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ProcurementService:
    """Enforce purchase order states and record stock changes atomically."""

    def __init__(self, repository: PurchaseOrderRepository) -> None:
        self.repository = repository

    def create(self, payload: CreateOrderInput) -> PurchaseOrderRecord:
        skus = [line.product_sku for line in payload.lines]
        if len(skus) != len(set(skus)):
            raise WorkflowError("Each product can appear only once in an order.", 422)
        with self.repository.transaction():
            supplier = self.repository.supplier(payload.supplier_id)
            if supplier is None:
                raise WorkflowError("Supplier was not found.", 404)
            for sku in skus:
                if self.repository.product(sku) is None:
                    raise WorkflowError(f"Product {sku} was not found.", 404)
                self.repository.link_supplier_product(supplier, sku)
            order = PurchaseOrderRecord(id=str(uuid4()), supplier_id=payload.supplier_id, status="draft", created_by=payload.actor.strip())
            order.lines = [PurchaseOrderLineRecord(id=str(uuid4()), product_sku=line.product_sku, ordered_quantity=line.quantity, received_quantity=0) for line in payload.lines]
            self.repository.add(order)
            self.repository.add(PurchaseOrderEventRecord(id=str(uuid4()), order_id=order.id, event="created", actor=payload.actor.strip()))
            self.repository.flush()
            return order

    def approve(self, order_id: str, actor: str) -> PurchaseOrderRecord:
        with self.repository.transaction():
            order = self.repository.order(order_id, lock=True)
            if order is None:
                raise WorkflowError("Purchase order was not found.", 404)
            if order.status != "draft":
                raise WorkflowError("Only draft orders can be approved.")
            order.status = "approved"
            self.repository.add(PurchaseOrderEventRecord(id=str(uuid4()), order_id=order.id, event="approved", actor=actor.strip()))
            self.repository.flush()
            return order

    def receive(self, order_id: str, payload: ReceiveOrderInput) -> PurchaseReceiptRecord:
        ids = [line.order_line_id for line in payload.lines]
        if len(ids) != len(set(ids)):
            raise WorkflowError("Each order line can appear only once in a receipt.", 422)
        try:
            with self.repository.transaction():
                order = self.repository.order(order_id, lock=True)
                if order is None:
                    raise WorkflowError("Purchase order was not found.", 404)
                if order.status not in ("approved", "partially_received"):
                    raise WorkflowError("Only approved orders can receive stock.")
                reference = payload.reference.strip()
                if self.repository.receipt_reference_exists(order_id, reference):
                    raise WorkflowError("This receipt reference has already been used for the order.")
                lines = {line.id: line for line in self.repository.lines(order_id, lock=True)}
                for received in payload.lines:
                    line = lines.get(received.order_line_id)
                    if line is None:
                        raise WorkflowError("Receipt line does not belong to this order.", 422)
                    if received.quantity > line.ordered_quantity - line.received_quantity:
                        raise WorkflowError("Received quantity exceeds the remaining order quantity.", 422)
                receipt = PurchaseReceiptRecord(id=str(uuid4()), order_id=order_id, reference=reference, received_by=payload.actor.strip())
                self.repository.add(receipt)
                for received in payload.lines:
                    line = lines[received.order_line_id]
                    product = self.repository.product(line.product_sku, lock=True)
                    if product is None:
                        raise WorkflowError("Product was not found.", 404)
                    receipt_line = PurchaseReceiptLineRecord(id=str(uuid4()), receipt_id=receipt.id, order_line_id=line.id, product_sku=line.product_sku, quantity=received.quantity)
                    receipt.lines.append(receipt_line)
                    line.received_quantity += received.quantity
                    product.stock += received.quantity
                    self.repository.add(StockMovementRecord(id=str(uuid4()), product_sku=line.product_sku, quantity_change=received.quantity, receipt_line_id=receipt_line.id))
                order.status = "received" if all(line.received_quantity == line.ordered_quantity for line in lines.values()) else "partially_received"
                self.repository.add(PurchaseOrderEventRecord(id=str(uuid4()), order_id=order_id, event="received", actor=payload.actor.strip()))
                self.repository.flush()
                return receipt
        except IntegrityError as error:
            raise WorkflowError("Receipt reference or stock movement already exists.") from error

    def list_orders(self) -> list[PurchaseOrderRecord]:
        return self.repository.orders()

    def get_order(self, order_id: str) -> PurchaseOrderRecord:
        order = self.repository.order(order_id)
        if order is None:
            raise WorkflowError("Purchase order was not found.", 404)
        return order

    def history(self, order_id: str):
        self.get_order(order_id)
        return self.repository.events(order_id), self.repository.receipts(order_id)

    def movements(self, sku: str | None = None):
        return self.repository.movements(sku)
