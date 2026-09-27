from app.schemas.base import ResponseModel


class CatalogSummary(ResponseModel):
    """Summary data shown on the dashboard and catalog page."""

    total_products: int
    available_items: int
