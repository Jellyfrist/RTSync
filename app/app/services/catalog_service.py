"""ชั้นบริการแค็ตตาล็อกที่คงไว้เพื่อรองรับ API เดิม"""

from app.repositories.catalog_repository import get_catalog_summary, list_products


def catalog_summary():
    """เรียกข้อมูลสรุป catalog ผ่าน repository"""

    return get_catalog_summary()


def products():
    """เรียกรายการสินค้าผ่าน service layer"""

    return list_products()
