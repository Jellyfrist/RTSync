from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
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
    address: dict = None
    system: str = ""
