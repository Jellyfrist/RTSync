"""รูปแบบข้อมูลซัพพลายเออร์"""

from pydantic import BaseModel


class Supplier(BaseModel):
    """ข้อมูลซัพพลายเออร์สำหรับ sourcing hub"""

    id: str
    name: str
    category: str
    description: str = ""
    delivery: str
    sku_count: int
