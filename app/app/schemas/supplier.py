"""รูปแบบข้อมูลซัพพลายเออร์"""

from pydantic import BaseModel, ConfigDict, Field


class SupplierCategoryCreate(BaseModel):
    """ข้อมูลหมวดหมู่ซัพพลายเออร์ที่ผู้ใช้เพิ่ม"""

    name: str = Field(min_length=1, max_length=100)


class SupplierCategoryOut(SupplierCategoryCreate):
    """ข้อมูลหมวดหมู่ซัพพลายเออร์ที่อ่านจากฐานข้อมูล"""

    model_config = ConfigDict(from_attributes=True)

    category_id: int


class Supplier(BaseModel):
    """ข้อมูลซัพพลายเออร์สำหรับ sourcing hub"""

    id: str
    name: str
    category: str
    description: str = ""
    delivery: str
    sku_count: int


class SupplierCreate(BaseModel):
    """ข้อมูลที่ใช้สร้างซัพพลายเออร์ใหม่"""

    name: str
    category: str
    description: str = ""
    delivery: str = "ไม่ระบุ"
