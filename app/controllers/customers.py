from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_customer_service
from app.models.customer import Customer as CustomerModel
from app.schemas.customer import Customer
from app.services.directory_service import DirectoryService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[Customer])
def get_customers(
    service: Annotated[DirectoryService[CustomerModel], Depends(get_customer_service)],
) -> list[CustomerModel]:
    return service.list()
