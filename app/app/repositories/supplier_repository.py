"""ข้อมูลตั้งต้นและฟังก์ชันอ่านข้อมูลซัพพลายเออร์"""

from app.schemas.supplier import Supplier


_SUPPLIERS = [
    Supplier(id="SUP-TH-001", name="บจก. ซันไซน์ โซล่า โซลูชั่น", category="Solar Panels", description="ตัวแทนหลัก Tier-1 แผงโซล่าเซลล์เกรดเอ", delivery="2-3 วัน", sku_count=48),
    Supplier(id="SUP-TH-004", name="บจก. สยาม ซีเคียวริตี้ ซัพพลาย", category="CCTV & Security", description="ศูนย์จำหน่ายอุปกรณ์กล้องวงจรปิด AI CCTV", delivery="1-2 วัน", sku_count=64),
    Supplier(id="SUP-TH-012", name="บมจ. กรีนเทค อิเล็คทริค อินดัสทรี", category="Electrical & Mounting", description="ผู้ผลิตตู้ Combiner Box และอุปกรณ์จับยึด", delivery="3-5 วัน", sku_count=82),
    Supplier(id="SUP-TH-019", name="บจก. ซันพาวเวอร์ ซัพพลาย แอนด์ เอ็นจิเนียริ่ง", category="Cabling & Protection", description="ตัวแทนจำหน่าย Inverter และ Energy Storage", delivery="1 วัน", sku_count=36),
]


def list_suppliers() -> list[Supplier]:
    """คืนรายการซัพพลายเออร์สำหรับ sourcing hub"""

    return _SUPPLIERS
