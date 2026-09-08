# RT Sync Backend

โครงสร้าง backend สำหรับระบบ RT Sync / RTStock ใช้ FastAPI และแบ่ง code ตามหน้าที่ของแต่ละชั้น

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

เอกสาร API จะอยู่ที่ `http://127.0.0.1:8000/docs`

## Current scope

- `GET /api/health` สำหรับตรวจสอบ service
- `GET /api/catalog/summary` สำหรับข้อมูลสรุป catalog ที่ frontend ใช้
- `GET /api/products` สำหรับรายการสินค้า mock
- `GET /api/customers` สำหรับรายการลูกค้า mock
- `GET /api/suppliers` สำหรับรายการซัพพลายเออร์ mock
- `GET /api/employees` สำหรับรายการพนักงาน mock

ข้อมูลปัจจุบันเก็บใน memory เพื่อเป็นโครงสร้างเริ่มต้น สามารถเปลี่ยน repository เป็น PostgreSQL/SQLAlchemy ได้ภายหลังโดยไม่ต้องย้าย router หรือ schema
