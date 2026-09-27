from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Product:
    """Product and stock data shown by the frontend."""

    sku: str
    name: str
    category: str
    stock: int
    price: Decimal
    unit: str = "ชิ้น"
    reorder_point: int = 0
    supplier_ids: tuple[str, ...] = ()
