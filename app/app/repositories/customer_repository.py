"""ข้อมูลตั้งต้นและฟังก์ชันอ่านข้อมูลลูกค้า"""

from app.schemas.customer import Customer


_CUSTOMERS = [
    Customer(id="089", code="CUST-2024-089", name="คุณสมศักดิ์ วัฒนากุล", phone="081-924-XXXX", location="อ.บางพลี จ.สมุทรปราการ", customer_type="บ้านพักอาศัย", status="ชำระครบถ้วน", system="10 kWp On-Grid (Huawei + Jinko)"),
    Customer(id="088", code="CUST-2024-088", name="บจก. ธนทรัพย์ โลจิสติกส์", phone="089-455-XXXX", location="นิคมฯ ลาดกระบัง กทม.", customer_type="ธุรกิจ/โรงงาน", status="รอตรวจรับงวด 2", system="120 kWp Zero-Export (Solis + Longi)"),
    Customer(id="087", code="CUST-2024-087", name="คุณกมลชนก สุขใจ", phone="086-321-XXXX", location="อ.เมือง จ.นนทบุรี", customer_type="บ้านพักอาศัย", status="ชำระครบถ้วน", system="5 kWp On-Grid (Huawei + Longi)"),
    Customer(id="086", code="CUST-2024-086", name="บริษัท พลังงานไทย จำกัด", phone="082-888-XXXX", location="อ.บางปะอิน จ.อยุธยา", customer_type="ธุรกิจ/โรงงาน", status="รอนัดตรวจเช็ก", system="80 kWp On-Grid (SMA + Jinko)"),
]


def list_customers() -> list[Customer]:
    """คืนรายการลูกค้าสำหรับ customer directory"""

    return _CUSTOMERS
