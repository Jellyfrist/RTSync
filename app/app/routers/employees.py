from fastapi import APIRouter

from app.repositories.employee_repository import list_employees
from app.schemas.employee import Employee

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[Employee])
def get_employees() -> list[Employee]:
    """ส่งรายการพนักงานให้ payroll workbench"""

    return list_employees()
