from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_supplier_service
from app.models.supplier import Supplier as SupplierModel
from app.schemas.supplier import CreateSupplierInput, Supplier
from app.dependencies import SessionDependency
from app.infrastructure.orm import SupplierRecord
from app.infrastructure.orm import ProductRecord, SupplierProductRecord
from app.schemas.product import Product
from uuid import uuid4
from app.services.directory_service import DirectoryService

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=list[Supplier])
def get_suppliers(
    service: Annotated[DirectoryService[SupplierModel], Depends(get_supplier_service)],
) -> list[SupplierModel]:
    return service.list()


@router.post("", status_code=201, response_model=Supplier)
def create_supplier(payload: CreateSupplierInput, session: SessionDependency):
    record = SupplierRecord(id=str(uuid4()), sku_count=0, **payload.model_dump())
    session.add(record)
    session.commit()
    return record


@router.post("/{supplier_id}/products/{sku}", response_model=Product)
def link_product(supplier_id: str, sku: str, session: SessionDependency):
    supplier = session.get(SupplierRecord, supplier_id)
    product = session.get(ProductRecord, sku)
    if supplier is None or product is None:
        raise HTTPException(status_code=404, detail="Supplier or product was not found.")
    if session.get(SupplierProductRecord, (supplier_id, sku)) is None:
        session.add(SupplierProductRecord(supplier_id=supplier_id, product_sku=sku))
        supplier.sku_count += 1
        session.commit()
        session.refresh(product)
    return product


@router.delete("/{supplier_id}/products/{sku}", status_code=204)
def unlink_product(supplier_id: str, sku: str, session: SessionDependency):
    link = session.get(SupplierProductRecord, (supplier_id, sku))
    if link is None:
        raise HTTPException(status_code=404, detail="Supplier product link was not found.")
    supplier = session.get(SupplierRecord, supplier_id)
    session.delete(link)
    if supplier is not None:
        supplier.sku_count = max(0, supplier.sku_count - 1)
    session.commit()
