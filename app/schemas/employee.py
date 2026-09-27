from app.schemas.base import ResponseModel
from decimal import Decimal


class Employee(ResponseModel):
    """Employee data used by payroll and overtime pages."""

    id: str
    name: str
    role: str
    salary: Decimal
    overtime_hours: float
