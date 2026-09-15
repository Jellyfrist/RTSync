"""ข้อมูลตั้งต้นและฟังก์ชันอ่านข้อมูลพนักงาน"""

from app.schemas.employee import Employee


_EMPLOYEES = [
    Employee(id="EMP-TH-014", name="สมนึก บุญส่ง", role="หัวหน้าช่างติดตั้งโซล่าเซลล์", salary=24000, overtime_hours=28, overtime_rate=250, allowance=1200, deduction=500, initials="สบ"),
    Employee(id="EMP-TH-021", name="ณัฐพล แสนสุข", role="ช่างติดตั้งไฟฟ้า Rooftop", salary=18500, overtime_hours=34.5, overtime_rate=180, allowance=800, initials="ณส"),
    Employee(id="EMP-TH-008", name="วราภรณ์ วงศ์ศิริ", role="วิศวกรออกแบบระบบ", salary=32000, overtime_hours=12, overtime_rate=300, allowance=1500, deduction=1200, initials="วว"),
    Employee(id="EMP-TH-019", name="กิตติชัย มั่นคง", role="เจ้าหน้าที่ตรวจสอบมาตรฐาน QA", salary=22000, overtime_hours=18, overtime_rate=200, allowance=600, initials="กม"),
]


def list_employees() -> list[Employee]:
    """คืนรายการพนักงานสำหรับ payroll workbench"""

    return _EMPLOYEES
