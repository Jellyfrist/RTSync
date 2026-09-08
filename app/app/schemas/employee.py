from pydantic import BaseModel


class Employee(BaseModel):
    """ข้อมูลพนักงานสำหรับหน้าค่าตอบแทนและ OT"""

    id: str
    name: str
    role: str
    salary: float
    overtime_hours: float
