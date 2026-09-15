"""ชั้นเข้าถึงข้อมูลสินค้า การเคลื่อนไหว และแจ้งเตือนคลัง"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inventory import Product, ReorderAlert, StockMovement
from app.schemas.inventory import ProductCreate, ProductUpdate


def product_status(product: Product) -> str:
    """คืนสถานะสินค้าตามจำนวนคงเหลือเทียบจุดสั่งซื้อ"""
    return "ต้องสั่งเพิ่ม" if product.current_stock <= product.reorder_point else "พร้อมจำหน่าย"


def list_products(db: Session) -> list[Product]:
    """เรียงและคืนรายการสินค้าทั้งหมด"""
    return list(db.scalars(select(Product).order_by(Product.created_at.desc())).all())


def get_product(db: Session, sku: str) -> Product | None:
    """ค้นหาสินค้าจากรหัส SKU"""
    return db.get(Product, sku)


def save_product(db: Session, payload: ProductCreate | ProductUpdate, existing: Product | None = None) -> Product:
    """เพิ่มหรือแก้ไขสินค้า แล้วปรับสถานะแจ้งเตือนให้สัมพันธ์กัน"""
    product = existing or Product(sku=payload.sku)
    product.product_name = payload.name
    product.category = payload.category
    product.unit = payload.unit
    product.unit_price = payload.price
    product.supplier = payload.supplier
    product.reorder_point = payload.reorder_point
    if existing is None:
        product.initial_stock = payload.stock
    product.current_stock = payload.stock
    db.add(product)
    db.flush()
    sync_alert(db, product)
    db.commit()
    db.refresh(product)
    return product


def receive_stock(db: Session, product: Product, quantity: int) -> Product:
    """เพิ่ม Stock และบันทึกประวัติการรับเข้า"""
    product.current_stock += quantity
    movement = StockMovement(
        sku=product.sku, movement_period=datetime.utcnow().strftime("%Y-%m"),
        received_quantity=quantity, issued_quantity=0, weekly_stock_quantity=product.current_stock,
        net_movement=quantity,
    )
    db.add(movement)
    sync_alert(db, product)
    db.commit()
    db.refresh(product)
    return product


def sync_alert(db: Session, product: Product) -> None:
    """สร้างหรือลบแจ้งเตือนตามระดับ Stock ล่าสุด"""
    alert = db.scalar(select(ReorderAlert).where(ReorderAlert.sku == product.sku))
    if product.current_stock <= product.reorder_point and alert is None:
        db.add(ReorderAlert(sku=product.sku))
    elif product.current_stock > product.reorder_point and alert is not None:
        db.delete(alert)


def list_alerts(db: Session) -> list[ReorderAlert]:
    """คืนรายการแจ้งเตือนจุดสั่งซื้อ"""
    return list(db.scalars(select(ReorderAlert).order_by(ReorderAlert.created_at.desc())).all())


def list_movements(db: Session) -> list[StockMovement]:
    """คืนประวัติการเคลื่อนไหวสินค้า"""
    return list(db.scalars(select(StockMovement).order_by(StockMovement.created_at.desc())).all())


def build_summary(db: Session) -> dict:
    """คำนวณค่ารวมที่ใช้แสดงบนแดชบอร์ดคลัง"""
    products = list_products(db)
    return {
        "total_products": len(products),
        "available_products": sum(product.current_stock > 0 for product in products),
        "inventory_value": sum(product.current_stock * product.unit_price for product in products),
        "reorder_alert_count": sum(product.current_stock <= product.reorder_point for product in products),
        "last_updated_at": datetime.utcnow(),
    }
