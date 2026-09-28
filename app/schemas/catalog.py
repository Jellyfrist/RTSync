from app.schemas.base import ResponseModel
from pydantic import BaseModel, Field


class CatalogSummary(ResponseModel):
    """Summary data shown on the dashboard and catalog page."""

    total_products: int
    available_items: int
    total_stock: int = 0
    low_stock: int = 0


class CategoryInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class CategoryOutput(ResponseModel):
    category_id: str
    name: str


class ReceiveStockInput(BaseModel):
    quantity: int = Field(gt=0)
    unit_cost: float = Field(default=0, ge=0)
