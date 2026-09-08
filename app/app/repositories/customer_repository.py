from app.schemas.customer import Customer


_CUSTOMERS = [
    Customer(id="089", code="CUST-2024-089", name="คุณสมศักดิ์ วัฒนากุล", phone="081-924-XXXX", location="อ.บางพลี จ.สมุทรปราการ", customer_type="บ้านพักอาศัย", status="ชำระครบถ้วน"),
    Customer(id="088", code="CUST-2024-088", name="บจก. ธนทรัพย์ โลจิสติกส์", phone="089-455-XXXX", location="นิคมฯ ลาดกระบัง กทม.", customer_type="ธุรกิจ/โรงงาน", status="รอตรวจรับงวด 2"),
]


def list_customers() -> list[Customer]:
    """คืนรายการลูกค้าสำหรับ customer directory"""

    return _CUSTOMERS
