"""Compatibility API for the data-management frontend.

The UI uses business-friendly resource names while the core API keeps the
catalog/procurement terminology.  These routes are a thin adapter; all state
is persisted through the same SQLAlchemy session and is never stored in the UI.
"""

from datetime import date
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import SessionDependency
from app.infrastructure.orm import (
    CategoryRecord, CustomerRecord, EmployeeRecord, OperationRecord,
    ProductRecord, SupplierCategoryRecord, SupplierRecord,
)
from app.schemas.catalog import CategoryInput, CategoryOutput, ReceiveStockInput
from app.schemas.customer import Customer, CustomerInput
from app.schemas.employee import Employee, EmployeeInput
from app.schemas.product import CreateProductInput, Product, UpdateProductInput
from app.schemas.supplier import CreateSupplierInput, Supplier

router = APIRouter(tags=["data-management"])


def _product(row: ProductRecord) -> Product:
    return Product.model_validate(row, from_attributes=True)


def _operation(row: OperationRecord) -> dict:
    return {**row.payload, "id": row.id, "status": row.status}


@router.get("/inventory/categories", response_model=list[CategoryOutput])
def inventory_categories(session: SessionDependency):
    return [CategoryOutput(category_id=row.id, name=row.name) for row in session.scalars(select(CategoryRecord).order_by(CategoryRecord.name))]


@router.post("/inventory/categories", status_code=201, response_model=CategoryOutput)
def create_inventory_category(payload: CategoryInput, session: SessionDependency):
    name = payload.name.strip()
    row = session.scalar(select(CategoryRecord).where(CategoryRecord.name == name))
    if row is None:
        row = CategoryRecord(id=f"CAT-{uuid4().hex[:12]}", name=name)
        session.add(row)
        session.commit()
    return CategoryOutput(category_id=row.id, name=row.name)


@router.get("/inventory/products", response_model=list[Product])
def inventory_products(session: SessionDependency):
    return [_product(row) for row in session.scalars(select(ProductRecord).order_by(ProductRecord.name))]


@router.post("/inventory/products", status_code=201, response_model=Product)
def create_inventory_product(payload: CreateProductInput, session: SessionDependency):
    if session.get(ProductRecord, payload.sku):
        raise HTTPException(status_code=409, detail="Product SKU already exists.")
    row = ProductRecord(**payload.model_dump())
    session.add(row)
    session.commit()
    return _product(row)


@router.put("/inventory/products/{sku}", response_model=Product)
def update_inventory_product(sku: str, payload: UpdateProductInput, session: SessionDependency):
    row = session.get(ProductRecord, sku)
    if row is None:
        raise HTTPException(status_code=404, detail="Product was not found.")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    session.commit()
    session.refresh(row)
    return _product(row)


@router.get("/inventory/summary")
def inventory_summary(session: SessionDependency):
    products = list(session.scalars(select(ProductRecord)))
    return {
        "total_products": len(products),
        "total_stock": sum(row.stock for row in products),
        "low_stock": sum(row.stock <= row.reorder_point for row in products),
    }


@router.post("/inventory/products/{sku}/receive", response_model=Product)
def inventory_receive(sku: str, payload: ReceiveStockInput, session: SessionDependency):
    row = session.get(ProductRecord, sku)
    if row is None:
        raise HTTPException(status_code=404, detail="Product was not found.")
    row.stock += payload.quantity
    row.cost_price = payload.unit_cost
    session.commit()
    session.refresh(row)
    return _product(row)


@router.get("/operations/{collection}")
def list_operations(collection: str, session: SessionDependency):
    rows = session.scalars(select(OperationRecord).where(OperationRecord.collection == collection).order_by(OperationRecord.created_at.desc()))
    return [_operation(row) for row in rows]


@router.post("/operations/{collection}", status_code=201)
def create_operation(collection: str, payload: dict, session: SessionDependency):
    row = OperationRecord(id=str(payload.get("id") or uuid4()), collection=collection, status=str(payload.get("status") or ""), payload=payload)
    session.add(row)
    session.commit()
    return _operation(row)


@router.patch("/operations/{collection}/{record_id}")
def update_operation(collection: str, record_id: str, payload: dict, session: SessionDependency):
    row = session.scalar(select(OperationRecord).where(OperationRecord.collection == collection, OperationRecord.id == record_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Operation record was not found.")
    row.payload = {**row.payload, **payload}
    row.status = str(row.payload.get("status") or "")
    session.commit()
    return _operation(row)


@router.get("/suppliers/categories", response_model=list[CategoryOutput])
def supplier_categories(session: SessionDependency):
    return [CategoryOutput(category_id=row.id, name=row.name) for row in session.scalars(select(SupplierCategoryRecord).order_by(SupplierCategoryRecord.name))]


@router.post("/suppliers/categories", status_code=201, response_model=CategoryOutput)
def create_supplier_category(payload: CategoryInput, session: SessionDependency):
    name = payload.name.strip()
    row = session.scalar(select(SupplierCategoryRecord).where(SupplierCategoryRecord.name == name))
    if row is None:
        row = SupplierCategoryRecord(id=f"SCAT-{uuid4().hex[:12]}", name=name)
        session.add(row)
        session.commit()
    return CategoryOutput(category_id=row.id, name=row.name)


@router.patch("/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: str, payload: CustomerInput, session: SessionDependency):
    row = session.get(CustomerRecord, customer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Customer was not found.")
    for key, value in payload.model_dump(exclude={"code"}).items():
        setattr(row, key, value)
    session.commit()
    return row


@router.post("/customers", status_code=201, response_model=Customer)
def create_customer(payload: CustomerInput, session: SessionDependency):
    code = payload.code or f"CUST-{uuid4().hex[:10].upper()}"
    row = CustomerRecord(id=str(uuid4()), code=code, **payload.model_dump(exclude={"code"}))
    session.add(row)
    session.commit()
    return row


@router.patch("/suppliers/{supplier_id}", response_model=Supplier)
def update_supplier(supplier_id: str, payload: CreateSupplierInput, session: SessionDependency):
    row = session.get(SupplierRecord, supplier_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Supplier was not found.")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    session.commit()
    return row


@router.post("/employees", status_code=201, response_model=Employee)
def create_employee(payload: EmployeeInput, session: SessionDependency):
    row = EmployeeRecord(id=f"EMP-{uuid4().hex[:10].upper()}", **payload.model_dump())
    session.add(row)
    session.commit()
    return row


@router.patch("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: str, payload: EmployeeInput, session: SessionDependency):
    row = session.get(EmployeeRecord, employee_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Employee was not found.")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    session.commit()
    return row
