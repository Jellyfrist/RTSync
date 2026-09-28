from app.schemas.base import ResponseModel


class Supplier(ResponseModel):
    """Supplier data used by the sourcing hub."""

    id: str
    name: str
    category: str
    delivery: str
    sku_count: int
    description: str = ""
    contact_name: str = ""
    contact_phone: str = ""
    contact_email: str = ""
    payment_terms: str = ""


from pydantic import BaseModel, Field


class CreateSupplierInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=120)
    delivery: str = Field(min_length=1, max_length=64)
    description: str = ""
    contact_name: str = ""
    contact_phone: str = ""
    contact_email: str = ""
    payment_terms: str = ""
