from app.schemas.supplier import Supplier


_SUPPLIERS = [
    Supplier(id="SUP-TH-001", name="บจก. ซันไซน์ โซล่า โซลูชั่น", category="Solar Panels", delivery="2-3 วัน", sku_count=48),
    Supplier(id="SUP-TH-004", name="บจก. สยาม ซีเคียวริตี้ ซัพพลาย", category="CCTV & Security", delivery="1-2 วัน", sku_count=64),
]


def list_suppliers() -> list[Supplier]:
    """คืนรายการซัพพลายเออร์สำหรับ sourcing hub"""

    return _SUPPLIERS
