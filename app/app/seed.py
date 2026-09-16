"""ข้อมูลตั้งต้นสำหรับสร้างฐานข้อมูลจำลองของระบบ"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Product, ProductCategory, ReorderAlert, StockMovement, SupplierCategory, SupplierRecord


# รายการสินค้าที่ใช้เติมฐานข้อมูลครั้งแรก
SEED_PRODUCTS = [
    {"sku": "SP-JA-550M", "name": "แผงโซลาร์ JA Solar 550W", "category": "แผงโซลาร์", "stock": 140, "reorder_point": 40, "unit": "แผง", "price": 4150, "supplier": "JA Solar Thailand"},
    {"sku": "INV-HW-5K1P", "name": "Huawei SUN2000-5KTL", "category": "อินเวอร์เตอร์", "stock": 12, "reorder_point": 15, "unit": "เครื่อง", "price": 42900, "supplier": "Huawei Solar"},
    {"sku": "INV-HW-10K3P", "name": "Huawei SUN2000-10KTL-M1", "category": "อินเวอร์เตอร์", "stock": 6, "reorder_point": 10, "unit": "เครื่อง", "price": 58900, "supplier": "Huawei Solar"},
    {"sku": "SP-LN-585X", "name": "Longi Hi-MO 6 585W", "category": "แผงโซลาร์", "stock": 84, "reorder_point": 35, "unit": "แผง", "price": 4350, "supplier": "LONGi Thailand"},
    {"sku": "SEN-HW-DTSU", "name": "Huawei Smart Power Sensor", "category": "อุปกรณ์วัด", "stock": 24, "reorder_point": 12, "unit": "ชิ้น", "price": 5200, "supplier": "Huawei Solar"},
    {"sku": "CB-DC-6MM", "name": "สายไฟโซลาร์ DC 6mm สีดำ", "category": "อุปกรณ์ติดตั้ง", "stock": 210, "reorder_point": 100, "unit": "ม้วน", "price": 1850, "supplier": "Solar Cable Co."},
]

SEED_SUPPLIERS = [
    {"id": "SUP-TH-001", "name": "JA Solar Thailand", "category": "Solar Panels", "description": "ผู้จัดจำหน่ายแผงโซลาร์ JA Solar", "delivery": "2-3 วัน"},
    {"id": "SUP-TH-012", "name": "Solar Cable Co.", "category": "Electrical & Mounting", "description": "อุปกรณ์สายไฟและงานติดตั้ง", "delivery": "3-5 วัน"},
    {"id": "SUP-TH-019", "name": "Huawei Solar", "category": "Inverter & Monitoring", "description": "อินเวอร์เตอร์และอุปกรณ์ตรวจวัด", "delivery": "1 วัน"},
    {"id": "SUP-TH-020", "name": "LONGi Thailand", "category": "Solar Panels", "description": "ผู้จัดจำหน่ายแผงโซลาร์ LONGi", "delivery": "2-3 วัน"},
]


def seed_inventory(db: Session) -> None:
    """เติมหมวดหมู่เสมอ และเติมสินค้าเฉพาะเมื่อฐานข้อมูลยังว่าง"""
    category_names = {item["category"] for item in SEED_PRODUCTS}
    category_names.update(db.scalars(select(Product.category).distinct()).all())
    existing_categories = set(db.scalars(select(ProductCategory.name)).all())
    for name in category_names - existing_categories:
        db.add(ProductCategory(name=name))
    supplier_category_names = {item["category"] for item in SEED_SUPPLIERS}
    supplier_category_names.update(db.scalars(select(SupplierRecord.category).distinct()).all())
    existing_supplier_categories = set(db.scalars(select(SupplierCategory.name)).all())
    for name in supplier_category_names - existing_supplier_categories:
        db.add(SupplierCategory(name=name))
    existing_suppliers = set(db.scalars(select(SupplierRecord.name)).all())
    for item in SEED_SUPPLIERS:
        if item["name"] not in existing_suppliers:
            db.add(SupplierRecord(**item))
    db.commit()

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
