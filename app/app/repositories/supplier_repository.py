"""ชั้นเข้าถึงข้อมูลซัพพลายเออร์จากฐานข้อมูล"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inventory import Product, SupplierCategory, SupplierRecord


def list_suppliers(db: Session) -> list[SupplierRecord]:
    """คืนซัพพลายเออร์ทั้งหมดจากฐานข้อมูล"""
    return list(db.scalars(select(SupplierRecord).order_by(SupplierRecord.name)).all())


def get_supplier_by_name(db: Session, name: str) -> SupplierRecord | None:
    """ค้นหาซัพพลายเออร์จากชื่อบริษัท"""
    return db.scalar(select(SupplierRecord).where(SupplierRecord.name == name))


def list_supplier_categories(db: Session) -> list[SupplierCategory]:
    """คืนหมวดหมู่ซัพพลายเออร์ทั้งหมดเรียงตามชื่อ"""
    return list(db.scalars(select(SupplierCategory).order_by(SupplierCategory.name)).all())


def get_supplier_category_by_name(db: Session, name: str) -> SupplierCategory | None:
    """ค้นหาหมวดหมู่ซัพพลายเออร์จากชื่อ"""
    return db.scalar(select(SupplierCategory).where(SupplierCategory.name == name))


def create_supplier_category(db: Session, name: str) -> SupplierCategory:
    """บันทึกหมวดหมู่ซัพพลายเออร์ใหม่"""
    category = SupplierCategory(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def create_supplier(db: Session, name: str, category: str, description: str, delivery: str) -> SupplierRecord:
    """บันทึกซัพพลายเออร์ใหม่และออกเลขที่อ้างอิง"""
    next_number = (db.scalar(select(func.count()).select_from(SupplierRecord)) or 0) + 20
    supplier = SupplierRecord(
        id=f"SUP-TH-{next_number:03d}", name=name, category=category,
        description=description, delivery=delivery,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def count_supplier_products(db: Session, supplier_name: str) -> int:
    """นับสินค้าที่ผูกกับซัพพลายเออร์ตามชื่อ"""
    return db.scalar(select(func.count()).select_from(Product).where(Product.supplier == supplier_name)) or 0
