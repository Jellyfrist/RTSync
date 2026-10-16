from app.schemas.base import ResponseModel
from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class Employee(ResponseModel):
    """Employee data used by payroll and overtime pages."""

    id: str
    name: str
    role: str
    phone: str = ""
    salary: Decimal
    overtime_hours: float
    email: str = ""
    start_date: date | None = None
    overtime_rate: Decimal = Decimal("0")
    allowance: Decimal = Decimal("0")
    deduction: Decimal = Decimal("0")


class EmployeeInput(BaseModel):
    name: str
    role: str
    phone: str = ""
    salary: Decimal = 0
    overtime_hours: float = 0
    email: str = ""
    start_date: date | None = None
    overtime_rate: Decimal = 0
    allowance: Decimal = 0
    deduction: Decimal = 0
