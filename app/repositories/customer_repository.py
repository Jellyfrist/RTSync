from app.infrastructure.orm import CustomerRecord
from app.models.customer import Customer
from app.repositories.base import SqlAlchemyRepository


class CustomerRepository(SqlAlchemyRepository):
    record_type = CustomerRecord

    def list(self) -> list[Customer]:
        return [Customer(row.id, row.code, row.name, row.phone, row.location, row.customer_type, row.status, row.email, row.tax_id, row.contact_name, row.address, row.system) for row in self.records()]
