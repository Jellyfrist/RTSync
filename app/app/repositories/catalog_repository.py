"""แหล่งข้อมูลแค็ตตาล็อกเดิมสำหรับ API ที่เข้ากันได้ย้อนหลัง"""

from app.schemas.catalog import CatalogSummary
from app.schemas.product import Product


_PRODUCTS = [
    Product(sku="SP-JA-550M", name="แผงโซลาร์ JA Solar 550W", category="แผงโซลาร์", stock=140, price=4150),
    Product(sku="INV-HW-5K1P", name="Huawei SUN2000-5KTL", category="อินเวอร์เตอร์", stock=12, price=42900),
    Product(sku="INV-HW-10K3P", name="Huawei SUN2000-10KTL-M1", category="อินเวอร์เตอร์", stock=6, price=58900),
]


def get_catalog_summary() -> CatalogSummary:
    """คำนวณสรุป catalog จากข้อมูลสินค้าใน repository"""

    return CatalogSummary(total_products=148, available_items=sum(product.stock for product in _PRODUCTS))


def list_products() -> list[Product]:
    """คืนรายการสินค้าเริ่มต้นสำหรับ API catalog"""

    return _PRODUCTS
