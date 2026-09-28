from app.schemas.base import ResponseModel
from pydantic import BaseModel


class Customer(ResponseModel):
    """Customer data used by the directory and customer profile."""

    id: str
    code: str
    name: str
    phone: str
    location: str
    customer_type: str
    status: str
    email: str = ""
    tax_id: str = ""
    contact_name: str = ""
    address: dict = {}
    system: str = ""


class CustomerInput(BaseModel):
    name: str
    phone: str
    location: str
    customer_type: str
    status: str = "รอเปิดบัญชี"
    code: str | None = None
    email: str = ""
    tax_id: str = ""
    contact_name: str = ""
    address: dict = {}
    system: str = ""
