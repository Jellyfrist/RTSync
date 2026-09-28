from app.schemas.base import ResponseModel
from decimal import Decimal
from pydantic import BaseModel, Field


class Product(ResponseModel):
    """Product and stock data shown by the frontend."""

    sku: str
    name: str
    category: str
    stock: int
    price: Decimal
    unit: str
    reorder_point: int
    supplier_ids: list[str] = Field(default_factory=list)
    cost_price: Decimal | None = None
    sale_price: Decimal | None = None


class CreateProductInput(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=120)
    unit: str = Field(default="ชิ้น", min_length=1, max_length=32)
    reorder_point: int = Field(default=0, ge=0)
    price: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    cost_price: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    sale_price: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)


class UpdateProductInput(CreateProductInput):
    pass
