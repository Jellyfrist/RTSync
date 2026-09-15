"""สร้าง engine, session และ dependency สำหรับเชื่อมฐานข้อมูล"""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """ฐานกลางของโมเดลฐานข้อมูลทั้งหมด"""


# ตำแหน่งฐานข้อมูล SQLite ที่สร้างอัตโนมัติในเครื่องนักพัฒนา
DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "rtsync.db"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.database_url or f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """เปิด session ให้ request ใช้ แล้วปิดเมื่อ request จบ"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
