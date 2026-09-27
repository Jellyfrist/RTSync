"""Build database sessions and application services."""
from collections.abc import Generator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.infrastructure.database import Database
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.product import Product
from app.models.supplier import Supplier
from app.repositories.base import ReadRepository
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.supplier_repository import SupplierRepository
from app.services.catalog_service import CatalogService
from app.services.directory_service import DirectoryService


@lru_cache(maxsize=1)
def get_database() -> Database:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required. Copy .env.example to .env and set the Supabase connection string.")
    return Database(settings.database_url)


def get_session(database: Annotated[Database, Depends(get_database)]) -> Generator[Session, None, None]:
    yield from database.session()


SessionDependency = Annotated[Session, Depends(get_session)]


def get_catalog_repository(session: SessionDependency) -> ReadRepository[Product]:
    return CatalogRepository(session)


def get_customer_repository(session: SessionDependency) -> ReadRepository[Customer]:
    return CustomerRepository(session)


def get_supplier_repository(session: SessionDependency) -> ReadRepository[Supplier]:
    return SupplierRepository(session)


def get_employee_repository(session: SessionDependency) -> ReadRepository[Employee]:
    return EmployeeRepository(session)


def get_catalog_service(
    repository: Annotated[ReadRepository[Product], Depends(get_catalog_repository)],
) -> CatalogService:
    return CatalogService(repository)


def get_customer_service(
    repository: Annotated[ReadRepository[Customer], Depends(get_customer_repository)],
) -> DirectoryService[Customer]:
    return DirectoryService(repository)


def get_supplier_service(
    repository: Annotated[ReadRepository[Supplier], Depends(get_supplier_repository)],
) -> DirectoryService[Supplier]:
    return DirectoryService(repository)


def get_employee_service(
    repository: Annotated[ReadRepository[Employee], Depends(get_employee_repository)],
) -> DirectoryService[Employee]:
    return DirectoryService(repository)
