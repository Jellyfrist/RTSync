from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Employee:
    """Employee data used by payroll and overtime pages."""

    id: str
    name: str
    role: str
    salary: Decimal
    overtime_hours: float
