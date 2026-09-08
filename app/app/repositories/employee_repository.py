from app.schemas.employee import Employee


_EMPLOYEES = [
    Employee(id="EMP-TH-014", name="สมนึก บุญส่ง", role="หัวหน้าช่างติดตั้งโซล่าเซลล์", salary=24000, overtime_hours=28),
    Employee(id="EMP-TH-021", name="ณัฐพล แสนสุข", role="ช่างติดตั้งไฟฟ้า Rooftop", salary=18500, overtime_hours=34.5),
]


def list_employees() -> list[Employee]:
    """คืนรายการพนักงานสำหรับ payroll workbench"""

    return _EMPLOYEES
