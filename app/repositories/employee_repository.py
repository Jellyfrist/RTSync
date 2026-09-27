from app.infrastructure.orm import EmployeeRecord
from app.models.employee import Employee
from app.repositories.base import SqlAlchemyRepository


class EmployeeRepository(SqlAlchemyRepository):
    record_type = EmployeeRecord

    def list(self) -> list[Employee]:
        return [Employee(row.id, row.name, row.role, row.salary, row.overtime_hours) for row in self.records()]
