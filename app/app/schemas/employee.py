"""รูปแบบข้อมูลพนักงานและค่าตอบแทน"""

from pydantic import BaseModel


class Employee(BaseModel):
    """ข้อมูลพนักงานสำหรับหน้าค่าตอบแทนและ OT"""

    id: str
    name: str
    role: str
    salary: float
    overtime_hours: float
    overtime_rate: float = 200
    allowance: float = 0
    deduction: float = 0
    initials: str = "พน"
