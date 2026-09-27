from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_catalog_service
from app.schemas.catalog import CatalogSummary
from app.schemas.product import CreateProductInput, Product
from app.dependencies import SessionDependency
from app.infrastructure.orm import ProductRecord
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.schemas.procurement import CreateStockIssueInput, StockIssueLineOutput, StockIssueOutput, StockMovementOutput
from app.services.catalog_service import CatalogService
from app.services.inventory_service import InventoryService
from app.services.procurement_service import WorkflowError

router = APIRouter(prefix="/catalog", tags=["catalog"])
Service = Annotated[CatalogService, Depends(get_catalog_service)]


@router.get("/summary", response_model=CatalogSummary)
def get_catalog_summary(service: Service):
    return service.summary()


@router.get("/products", response_model=list[Product])
def get_products(service: Service):
    return service.list()


@router.post("/products", status_code=201, response_model=Product)
def create_product(payload: CreateProductInput, session: SessionDependency):
    if session.get(ProductRecord, payload.sku) is not None:
        raise HTTPException(status_code=409, detail="Product SKU already exists.")
    record = ProductRecord(sku=payload.sku, name=payload.name, category=payload.category, unit=payload.unit,
                           reorder_point=payload.reorder_point, price=payload.price, stock=0)
    session.add(record)
    session.commit()
    return record


@router.get("/stock-movements", response_model=list[StockMovementOutput])
def get_stock_movements(session: SessionDependency, sku: str | None = None):
    return PurchaseOrderRepository(session).movements(sku)


@router.post("/stock-issues", status_code=201, response_model=StockIssueOutput)
def issue_stock(payload: CreateStockIssueInput, session: SessionDependency):
    try:
        issue = InventoryService(session).issue(payload)
    except WorkflowError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return StockIssueOutput(id=issue.id, reference=issue.reference, actor=issue.actor, created_at=issue.created_at,
                            lines=[StockIssueLineOutput(product_sku=line.product_sku, quantity=line.quantity) for line in issue.lines])
