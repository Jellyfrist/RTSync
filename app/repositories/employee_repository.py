from app.infrastructure.orm import EmployeeRecord
from app.models.employee import Employee
from app.repositories.base import SqlAlchemyRepository


class EmployeeRepository(SqlAlchemyRepository):
    record_type = EmployeeRecord

    def list(self) -> list[Employee]:
        return [
            Employee(
                row.id,
                row.name,
                row.role,
                row.salary,
                row.overtime_hours,
                row.email,
                row.start_date,
                row.overtime_rate,
                row.allowance,
                row.deduction,
                row.phone,
            )
            for row in self.records()
        ]
