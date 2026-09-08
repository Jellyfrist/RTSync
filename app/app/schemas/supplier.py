from pydantic import BaseModel


class Supplier(BaseModel):
    """ข้อมูลซัพพลายเออร์สำหรับ sourcing hub"""

    id: str
    name: str
    category: str
    delivery: str
    sku_count: int
