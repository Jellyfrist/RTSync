"""จุดเริ่มต้นของ FastAPI และจุดรวม router ของทุกโมดูล"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import catalog, customers, employees, health, inventory, operations, suppliers
from app.seed import seed_inventory
from app.models import inventory as inventory_models  # noqa: F401 - ลงทะเบียนโมเดลกับ metadata


# สร้าง FastAPI application และรวม router ของแต่ละโมดูลธุรกิจ
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(catalog.router, prefix=settings.api_prefix)
app.include_router(customers.router, prefix=settings.api_prefix)
app.include_router(suppliers.router, prefix=settings.api_prefix)
app.include_router(employees.router, prefix=settings.api_prefix)
app.include_router(inventory.router, prefix=settings.api_prefix)
app.include_router(operations.router, prefix=settings.api_prefix)


@app.on_event("startup")
def initialize_database() -> None:
    """สร้างตารางและเติมข้อมูลตั้งต้นครั้งแรกที่ backend เริ่มทำงาน"""

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_inventory(db)
