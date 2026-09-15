"""รูปแบบข้อมูลลูกค้าที่ส่งให้หน้าจัดการลูกค้า"""

from pydantic import BaseModel


class Customer(BaseModel):
    """ข้อมูลลูกค้าที่ใช้ใน directory และ customer profile"""

    id: str
    code: str
    name: str
    phone: str
    location: str
    customer_type: str
    status: str
    system: str = "ยังไม่มีข้อมูลระบบ"
