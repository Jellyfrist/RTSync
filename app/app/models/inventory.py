"""โมเดลฐานข้อมูลตาม ERD ของระบบจัดการสินค้าและคลัง"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    """ตารางสินค้าและค่าคงคลังปัจจุบัน"""
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(String(40), primary_key=True)
    product_name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    supplier: Mapped[str] = mapped_column(String(160), nullable=False, default="ไม่ระบุ")
    unit: Mapped[str] = mapped_column(String(30), nullable=False, default="ชิ้น")
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    initial_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    movements: Mapped[list["StockMovement"]] = relationship(back_populates="product")
    reorder_alerts: Mapped[list["ReorderAlert"]] = relationship(back_populates="product")


class StockMovement(Base):
    """ตารางประวัติรับเข้าและเบิกออกสินค้า"""
    __tablename__ = "stock_movements"

    movement_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(ForeignKey("products.sku"), nullable=False)
    movement_period: Mapped[str] = mapped_column(String(20), nullable=False)
    received_quantity: Mapped[int] = mapped_column(Integer, default=0)
    issued_quantity: Mapped[int] = mapped_column(Integer, default=0)
    weekly_stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    net_movement: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped[Product] = relationship(back_populates="movements")


class ReorderAlert(Base):
    """ตารางแจ้งเตือนสินค้าที่ต่ำกว่าจุดสั่งซื้อ"""
    __tablename__ = "reorder_alerts"

    alert_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(ForeignKey("products.sku"), nullable=False)
    purchase_order_status: Mapped[str] = mapped_column(String(40), default="ยังไม่ได้สั่งซื้อ")
    reorder_status: Mapped[str] = mapped_column(String(40), default="ต้องสั่งเพิ่ม")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped[Product] = relationship(back_populates="reorder_alerts")
