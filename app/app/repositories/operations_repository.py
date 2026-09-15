"""แหล่งข้อมูลตั้งต้นของงานขาย ติดตั้ง และบริการหลังการขาย"""

from app.schemas.operations import Appointment, CatalogItem, ServiceTicket


def list_catalog() -> list[CatalogItem]:
    """คืนสินค้าแนะนำสำหรับงานขาย"""
    return [
        CatalogItem(sku="SP-LN-550", name="แผงโซลาร์ Longi 550W", price=4150, stock=18, unit="แผง"),
        CatalogItem(sku="INV-HW-10K", name="Inverter Huawei 10kW 3P", price=58900, stock=6, unit="เครื่อง"),
        CatalogItem(sku="BAT-BYD-10", name="แบตเตอรี่ BYD 10.2kWh", price=165000, stock=3, unit="ชุด"),
    ]


def list_appointments() -> list[Appointment]:
    """คืนคิวนัดหมายติดตั้งตั้งต้น"""
    return [
        Appointment(id="INS-250615", customer="คุณสมศักดิ์ วัฒนากุล", site="บางพลี สมุทรปราการ", date="18 มิ.ย. 2025", time="09:00–12:00", crew="ทีมช่าง A", status="ยืนยันแล้ว", type="ติดตั้งระบบ 10 kWp"),
        Appointment(id="INS-250617", customer="บริษัท พลังงานไทย จำกัด", site="บางปะอิน อยุธยา", date="20 มิ.ย. 2025", time="13:00–16:00", crew="ทีมช่าง B", status="รอยืนยัน", type="ตรวจหน้างานก่อนติดตั้ง"),
        Appointment(id="INS-250620", customer="บจก. ธนทรัพย์ โลจิสติกส์", site="ลาดกระบัง กทม.", date="23 มิ.ย. 2025", time="09:00–15:00", crew="ทีมช่าง C", status="เตรียมอุปกรณ์", type="ติดตั้งระบบ 120 kWp"),
    ]


def list_service_tickets() -> list[ServiceTicket]:
    """คืนใบงานบริการตั้งต้น"""
    return [
        ServiceTicket(id="SRV-25042", customer="คุณกมลชนก สุขใจ", subject="Monitoring ไม่ส่งข้อมูล", opened="16 มิ.ย. 2025", priority="สูง", status="กำลังดำเนินการ", owner="ช่างณัฐพล"),
        ServiceTicket(id="SRV-25039", customer="คุณสมศักดิ์ วัฒนากุล", subject="ตรวจเช็กประจำปี", opened="12 มิ.ย. 2025", priority="ปกติ", status="เสร็จสิ้น", owner="ทีมช่าง A"),
    ]
