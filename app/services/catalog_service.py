from app.models.catalog import CatalogSummary
from app.models.product import Product
from app.services.directory_service import DirectoryService


class CatalogService(DirectoryService[Product]):
    def summary(self) -> CatalogSummary:
        products = self.list()
        return CatalogSummary(
            total_products=len(products),
            available_items=sum(product.stock for product in products),
        )
