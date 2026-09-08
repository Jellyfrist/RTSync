from pydantic import BaseModel


class Product(BaseModel):
    """ข้อมูลสินค้าและจำนวนคงคลังที่ frontend ใช้แสดงผล"""

    sku: str
    name: str
    category: str
    stock: int
    price: float
