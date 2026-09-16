"""เส้นทาง API สำหรับสินค้า สต็อก การเคลื่อนไหว และแจ้งเตือน"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.inventory_repository import build_summary, list_alerts, list_categories, list_movements, list_products, product_status
from app.schemas.inventory import InventorySummary, ProductCategoryCreate, ProductCategoryOut, ProductCreate, ProductOut, ProductUpdate, ReorderAlertOut, StockMovementOut, StockReceive
from app.services.inventory_service import create_category, create_product, receive_product_stock, update_product


router = APIRouter(prefix="/inventory", tags=["inventory"])


def serialize_product(product) -> ProductOut:
    """แปลงโมเดลฐานข้อมูลเป็นรูปแบบข้อมูลที่ frontend ใช้"""
    return ProductOut(
        sku=product.sku, name=product.product_name, category=product.category, unit=product.unit,
        price=product.unit_price, supplier=product.supplier, stock=product.current_stock,
        reorder_point=product.reorder_point, status=product_status(product),
    )


@router.get("/summary", response_model=InventorySummary)
def get_summary(db: Session = Depends(get_db)):
    """ส่งตัวเลขสรุปคลัง"""
    return build_summary(db)


@router.get("/products", response_model=list[ProductOut])
def get_products(db: Session = Depends(get_db)):
    """ส่งรายการสินค้า"""
    return [serialize_product(product) for product in list_products(db)]


@router.get("/categories", response_model=list[ProductCategoryOut])
def get_categories(db: Session = Depends(get_db)):
    """ส่งรายการหมวดหมู่สินค้าจากฐานข้อมูล"""
    return list_categories(db)


@router.post("/categories", response_model=ProductCategoryOut, status_code=status.HTTP_201_CREATED)
def post_category(payload: ProductCategoryCreate, db: Session = Depends(get_db)):
    """เพิ่มหมวดหมู่สินค้าใหม่"""
    return create_category(db, payload.name)


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def post_product(payload: ProductCreate, db: Session = Depends(get_db)):
    """รับคำขอสร้างสินค้า"""
    return serialize_product(create_product(db, payload))


@router.put("/products/{sku}", response_model=ProductOut)
def put_product(sku: str, payload: ProductUpdate, db: Session = Depends(get_db)):
    """รับคำขอแก้ไขสินค้า"""
    return serialize_product(update_product(db, sku, payload))


@router.post("/products/{sku}/receive", response_model=ProductOut)
def post_receive(sku: str, payload: StockReceive, db: Session = Depends(get_db)):
    """รับคำขอเติม Stock"""
    return serialize_product(receive_product_stock(db, sku, payload.quantity))


@router.get("/movements", response_model=list[StockMovementOut])
def get_movements(db: Session = Depends(get_db)):
    """ส่งประวัติการเคลื่อนไหว"""
    return list_movements(db)


@router.get("/alerts", response_model=list[ReorderAlertOut])
def get_alerts(db: Session = Depends(get_db)):
    """ส่งรายการสินค้าที่ต้องสั่งเพิ่ม"""
    return [
        ReorderAlertOut(
            alert_id=alert.alert_id, sku=alert.sku, product_name=alert.product.product_name,
            current_stock=alert.product.current_stock, reorder_point=alert.product.reorder_point,
            purchase_order_status=alert.purchase_order_status, reorder_status=alert.reorder_status,
        )
        for alert in list_alerts(db)
    ]
