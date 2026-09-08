from fastapi import APIRouter

from app.repositories.customer_repository import list_customers
from app.schemas.customer import Customer

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[Customer])
def get_customers() -> list[Customer]:
    """ส่งรายการลูกค้าให้ customer directory"""

    return list_customers()
