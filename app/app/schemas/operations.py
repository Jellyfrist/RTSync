"""รูปแบบข้อมูลของแค็ตตาล็อก นัดหมาย และใบงานบริการ"""

from pydantic import BaseModel


class CatalogItem(BaseModel):
    sku: str
    name: str
    price: float
    stock: int
    unit: str


class Appointment(BaseModel):
    id: str
    customer: str
    site: str
    date: str
    time: str
    crew: str
    status: str
    type: str


class ServiceTicket(BaseModel):
    id: str
    customer: str
    subject: str
    opened: str
    priority: str
    status: str
    owner: str
