"""เส้นทาง API สำหรับงานขาย นัดหมายติดตั้ง และบริการหลังการขาย"""

from fastapi import APIRouter

from app.repositories.operations_repository import list_appointments, list_catalog, list_service_tickets
from app.schemas.operations import Appointment, CatalogItem, ServiceTicket


router = APIRouter(prefix="/operations", tags=["operations"])


@router.get("/catalog", response_model=list[CatalogItem])
def get_catalog():
    """ส่งแค็ตตาล็อกสินค้าที่ใช้ทำใบเสนอราคา"""
    return list_catalog()


@router.get("/appointments", response_model=list[Appointment])
def get_appointments():
    """ส่งรายการนัดหมายติดตั้ง"""
    return list_appointments()


@router.get("/service-tickets", response_model=list[ServiceTicket])
def get_service_tickets():
    """ส่งรายการใบงานบริการ"""
    return list_service_tickets()
