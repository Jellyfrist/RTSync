from dataclasses import dataclass


@dataclass(frozen=True)
class Supplier:
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
