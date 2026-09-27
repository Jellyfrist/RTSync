from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_employee_service
from app.models.employee import Employee as EmployeeModel
from app.schemas.employee import Employee
from app.services.directory_service import DirectoryService

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[Employee])
def get_employees(
    service: Annotated[DirectoryService[EmployeeModel], Depends(get_employee_service)],
) -> list[EmployeeModel]:
    return service.list()
