"""ข้อมูลตั้งต้นสำหรับสร้างฐานข้อมูลจำลองของระบบ"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Product, ReorderAlert, StockMovement


# รายการสินค้าที่ใช้เติมฐานข้อมูลครั้งแรก
SEED_PRODUCTS = [
    {"sku": "SP-JA-550M", "name": "แผงโซลาร์ JA Solar 550W", "category": "แผงโซลาร์", "stock": 140, "reorder_point": 40, "unit": "แผง", "price": 4150, "supplier": "JA Solar Thailand"},
    {"sku": "INV-HW-5K1P", "name": "Huawei SUN2000-5KTL", "category": "อินเวอร์เตอร์", "stock": 12, "reorder_point": 15, "unit": "เครื่อง", "price": 42900, "supplier": "Huawei Solar"},
    {"sku": "INV-HW-10K3P", "name": "Huawei SUN2000-10KTL-M1", "category": "อินเวอร์เตอร์", "stock": 6, "reorder_point": 10, "unit": "เครื่อง", "price": 58900, "supplier": "Huawei Solar"},
    {"sku": "SP-LN-585X", "name": "Longi Hi-MO 6 585W", "category": "แผงโซลาร์", "stock": 84, "reorder_point": 35, "unit": "แผง", "price": 4350, "supplier": "LONGi Thailand"},
    {"sku": "SEN-HW-DTSU", "name": "Huawei Smart Power Sensor", "category": "อุปกรณ์วัด", "stock": 24, "reorder_point": 12, "unit": "ชิ้น", "price": 5200, "supplier": "Huawei Solar"},
    {"sku": "CB-DC-6MM", "name": "สายไฟโซลาร์ DC 6mm สีดำ", "category": "อุปกรณ์ติดตั้ง", "stock": 210, "reorder_point": 100, "unit": "ม้วน", "price": 1850, "supplier": "Solar Cable Co."},
]


def seed_inventory(db: Session) -> None:
    """เติมสินค้าและแจ้งเตือนเฉพาะเมื่อฐานข้อมูลยังไม่มีสินค้า"""
    if db.scalar(select(Product.sku).limit(1)):
        return
    for item in SEED_PRODUCTS:
        product = Product(
            sku=item["sku"], product_name=item["name"], category=item["category"],
            supplier=item["supplier"], unit=item["unit"], unit_price=item["price"],
            initial_stock=item["stock"], current_stock=item["stock"], reorder_point=item["reorder_point"],
        )
        db.add(product)
        if item["stock"] <= item["reorder_point"]:
            db.add(ReorderAlert(sku=item["sku"]))
    db.commit()
