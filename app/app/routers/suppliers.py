"""เส้นทาง API รายชื่อซัพพลายเออร์"""

from fastapi import APIRouter

from app.repositories.supplier_repository import list_suppliers
from app.schemas.supplier import Supplier

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=list[Supplier])
def get_suppliers() -> list[Supplier]:
    """ส่งรายการซัพพลายเออร์ให้หน้า sourcing"""
    """ส่งรายการซัพพลายเออร์ให้ sourcing hub"""

    return list_suppliers()
