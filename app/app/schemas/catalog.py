from pydantic import BaseModel


class CatalogSummary(BaseModel):
    """ข้อมูลสรุปที่แสดงบน dashboard และหน้า catalog"""

    total_products: int
    available_items: int
