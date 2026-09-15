"""กฎธุรกิจสำหรับเพิ่ม แก้ไข และเติมสินค้า"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.inventory_repository import get_product, save_product, receive_stock
from app.schemas.inventory import ProductCreate, ProductUpdate


def create_product(db: Session, payload: ProductCreate):
    """ตรวจ SKU ซ้ำก่อนสร้างสินค้าใหม่"""
    if get_product(db, payload.sku):
        raise HTTPException(status_code=409, detail="SKU นี้มีอยู่แล้ว")
    return save_product(db, payload)


def update_product(db: Session, sku: str, payload: ProductUpdate):
    """ค้นหาและบันทึกการแก้ไขสินค้า"""
    product = get_product(db, sku)
    if not product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")
    return save_product(db, payload, product)


def receive_product_stock(db: Session, sku: str, quantity: int):
    """ตรวจสินค้าแล้วส่งจำนวนรับเข้าไปบันทึก"""
    product = get_product(db, sku)
    if not product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")
    return receive_stock(db, product, quantity)
