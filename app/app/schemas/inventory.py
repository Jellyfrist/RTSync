"""รูปแบบข้อมูล request/response ของโมดูลคลังสินค้า"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    sku: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=160)
    category: str
    unit: str = "ชิ้น"
    price: float = Field(default=0, ge=0)
    supplier: str = "ไม่ระบุ"
    stock: int = Field(default=0, ge=0)
    reorder_point: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class ProductCategoryOut(ProductCategoryCreate):
    model_config = ConfigDict(from_attributes=True)

    category_id: int


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    status: str


class StockReceive(BaseModel):
    quantity: int = Field(gt=0)


class StockMovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    movement_id: int
    sku: str
    movement_period: str
    received_quantity: int
    issued_quantity: int
    weekly_stock_quantity: int
    net_movement: int
    created_at: datetime


class ReorderAlertOut(BaseModel):
    alert_id: int
    sku: str
    product_name: str
    current_stock: int
    reorder_point: int
    purchase_order_status: str
    reorder_status: str


class InventorySummary(BaseModel):
    total_products: int
    available_products: int
    inventory_value: float
    reorder_alert_count: int
    last_updated_at: datetime
