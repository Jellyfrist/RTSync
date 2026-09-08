from fastapi import APIRouter

from app.schemas.catalog import CatalogSummary
from app.schemas.product import Product
from app.services.catalog_service import catalog_summary, products

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/summary", response_model=CatalogSummary)
def get_catalog_summary() -> CatalogSummary:
    """ส่งข้อมูลสรุป catalog ให้ dashboard และหน้า inventory"""

    return catalog_summary()


@router.get("/products", response_model=list[Product])
def get_products() -> list[Product]:
    """ส่งรายการสินค้าเริ่มต้นให้หน้า inventory"""

    return products()
