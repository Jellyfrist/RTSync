from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogSummary:
    """Summary data shown on the dashboard and catalog page."""

    total_products: int
    available_items: int
    total_stock: int = 0
    low_stock: int = 0
