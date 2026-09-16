"""เส้นทาง API รายชื่อซัพพลายเออร์"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.supplier_repository import (
    count_supplier_products,
    create_supplier,
    create_supplier_category,
    get_supplier_by_name,
    get_supplier_category_by_name,
    list_supplier_categories,
    list_suppliers,
)
from app.schemas.supplier import Supplier, SupplierCategoryCreate, SupplierCategoryOut, SupplierCreate

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


def serialize_supplier(supplier, db: Session) -> Supplier:
    """แปลงข้อมูลฐานข้อมูลเป็นรูปแบบที่ frontend ใช้"""
    return Supplier(
        id=supplier.id, name=supplier.name, category=supplier.category,
        description=supplier.description, delivery=supplier.delivery,
        sku_count=count_supplier_products(db, supplier.name),
    )


@router.get("", response_model=list[Supplier])
def get_suppliers(db: Session = Depends(get_db)) -> list[Supplier]:
    """ส่งรายการซัพพลายเออร์ให้หน้า sourcing"""
    """ส่งรายการซัพพลายเออร์ให้ sourcing hub"""

    return [serialize_supplier(supplier, db) for supplier in list_suppliers(db)]


@router.get("/categories", response_model=list[SupplierCategoryOut])
def get_supplier_categories(db: Session = Depends(get_db)) -> list[SupplierCategoryOut]:
    """ส่งรายการหมวดหมู่ซัพพลายเออร์จากฐานข้อมูล"""
    return list_supplier_categories(db)


@router.post("/categories", response_model=SupplierCategoryOut, status_code=status.HTTP_201_CREATED)
def post_supplier_category(
    payload: SupplierCategoryCreate, db: Session = Depends(get_db)
) -> SupplierCategoryOut:
    """เพิ่มหมวดหมู่ซัพพลายเออร์ใหม่และป้องกันชื่อซ้ำ"""
    name = payload.name.strip()
    if get_supplier_category_by_name(db, name):
        raise HTTPException(status_code=409, detail="หมวดหมู่ซัพพลายเออร์นี้มีอยู่แล้ว")
    return create_supplier_category(db, name)


@router.post("", response_model=Supplier, status_code=status.HTTP_201_CREATED)
def post_supplier(payload: SupplierCreate, db: Session = Depends(get_db)) -> Supplier:
    """เพิ่มซัพพลายเออร์ใหม่ลงฐานข้อมูล"""
    name = payload.name.strip()
    category = payload.category.strip()
    if get_supplier_by_name(db, name):
        raise HTTPException(status_code=409, detail="ซัพพลายเออร์นี้มีอยู่แล้ว")
    if not get_supplier_category_by_name(db, category):
        raise HTTPException(status_code=422, detail="กรุณาเลือกหมวดหมู่ซัพพลายเออร์จากรายการ")
    supplier = create_supplier(db, name, category, payload.description.strip(), payload.delivery.strip())
    return serialize_supplier(supplier, db)
