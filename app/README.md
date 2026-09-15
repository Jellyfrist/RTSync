# RT Sync Backend

โครงสร้าง backend สำหรับระบบ RT Sync / RTStock ใช้ FastAPI และแบ่ง code ตามหน้าที่ของแต่ละชั้น

## Run locally

```bash
cd app
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

ข้อมูล inventory ใช้ SQLite ในโฟลเดอร์ `app/data` และ seed อัตโนมัติเมื่อเริ่มระบบ สามารถเปลี่ยน `DATABASE_URL` ใน `.env` เป็น PostgreSQL ได้ โดยยังคงแยก router → service → repository → model/schema เหมือนเดิม
