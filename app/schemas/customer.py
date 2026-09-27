from app.schemas.base import ResponseModel


class Customer(ResponseModel):
    """Customer data used by the directory and customer profile."""

    id: str
    code: str
    name: str
    phone: str
    location: str
    customer_type: str
    status: str
