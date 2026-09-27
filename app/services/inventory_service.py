"""Record outbound stock issues and their ledger entries atomically."""

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure.orm import ProductRecord, StockIssueLineRecord, StockIssueRecord, StockMovementRecord
from app.schemas.procurement import CreateStockIssueInput
from app.services.procurement_service import WorkflowError


class InventoryService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def issue(self, payload: CreateStockIssueInput) -> StockIssueRecord:
        skus = [line.product_sku for line in payload.lines]
        if len(skus) != len(set(skus)):
            raise WorkflowError("Each product can appear only once in an issue.", 422)
        reference = payload.reference.strip()
        actor = payload.actor.strip()
        if not reference or not actor:
            raise WorkflowError("Reference and actor are required.", 422)
        try:
            with self.session.begin():
                if self.session.scalar(select(StockIssueRecord.id).where(StockIssueRecord.reference == reference)):
                    raise WorkflowError("Stock issue reference already exists.")
                products = {
                    product.sku: product for product in self.session.scalars(
                        select(ProductRecord).where(ProductRecord.sku.in_(skus)).order_by(ProductRecord.sku).with_for_update()
                    )
                }
                for line in payload.lines:
                    product = products.get(line.product_sku)
                    if product is None:
                        raise WorkflowError(f"Product {line.product_sku} was not found.", 404)
                    if product.stock < line.quantity:
                        raise WorkflowError(f"Insufficient stock for {line.product_sku}.")
                issue = StockIssueRecord(id=str(uuid4()), reference=reference, actor=actor)
                self.session.add(issue)
                for line in payload.lines:
                    issue_line = StockIssueLineRecord(id=str(uuid4()), issue_id=issue.id,
                                                      product_sku=line.product_sku, quantity=line.quantity)
                    issue.lines.append(issue_line)
                    products[line.product_sku].stock -= line.quantity
                    self.session.add(StockMovementRecord(id=str(uuid4()), product_sku=line.product_sku,
                                                         quantity_change=-line.quantity, issue_line_id=issue_line.id))
                self.session.flush()
                return issue
        except IntegrityError as error:
            raise WorkflowError("Stock issue reference already exists.") from error
