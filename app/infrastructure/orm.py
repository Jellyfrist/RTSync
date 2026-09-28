from datetime import date, datetime, timezone

from decimal import Decimal

from sqlalchemy import JSON, CheckConstraint, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class BaseModel(Base):
    """Base for database records."""

    __abstract__ = True


class ProductRecord(BaseModel):
    __tablename__ = "products"
    __table_args__ = (CheckConstraint("stock >= 0", name="ck_product_stock_nonnegative"),)

    sku: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False, default="ชิ้น")
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    cost_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    sale_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    supplier_links: Mapped[list["SupplierProductRecord"]] = relationship(back_populates="product", cascade="all, delete-orphan")

    @property
    def supplier_ids(self) -> list[str]:
        return [link.supplier_id for link in self.supplier_links]


class CustomerRecord(BaseModel):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(64), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_type: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    tax_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    address: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    system: Mapped[str] = mapped_column(String(255), nullable=False, default="")


class SupplierRecord(BaseModel):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    delivery: Mapped[str] = mapped_column(String(64), nullable=False)
    sku_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    contact_phone: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    payment_terms: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    product_links: Mapped[list["SupplierProductRecord"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")


class SupplierProductRecord(BaseModel):
    __tablename__ = "supplier_products"

    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), primary_key=True)
    product_sku: Mapped[str] = mapped_column(ForeignKey("products.sku"), primary_key=True)
    supplier: Mapped[SupplierRecord] = relationship(back_populates="product_links")
    product: Mapped[ProductRecord] = relationship(back_populates="supplier_links")


class EmployeeRecord(BaseModel):
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    salary: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    email: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    overtime_rate: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    allowance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    deduction: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)


class CategoryRecord(BaseModel):
    __tablename__ = "inventory_categories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class SupplierCategoryRecord(BaseModel):
    __tablename__ = "supplier_categories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class OperationRecord(BaseModel):
    """Persist UI workflows whose fields evolve independently from core inventory."""

    __tablename__ = "operations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    collection: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class PurchaseOrderRecord(BaseModel):
    __tablename__ = "purchase_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="draft")
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    lines: Mapped[list["PurchaseOrderLineRecord"]] = relationship(back_populates="order", cascade="all, delete-orphan", order_by="PurchaseOrderLineRecord.id")


class PurchaseOrderLineRecord(BaseModel):
    __tablename__ = "purchase_order_lines"
    __table_args__ = (
        UniqueConstraint("order_id", "product_sku", name="uq_order_product"),
        CheckConstraint("ordered_quantity > 0", name="ck_ordered_quantity_positive"),
        CheckConstraint("received_quantity >= 0 AND received_quantity <= ordered_quantity", name="ck_received_quantity_range"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False)
    product_sku: Mapped[str] = mapped_column(ForeignKey("products.sku"), nullable=False)
    ordered_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    received_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    order: Mapped[PurchaseOrderRecord] = relationship(back_populates="lines")


class PurchaseReceiptRecord(BaseModel):
    __tablename__ = "purchase_receipts"
    __table_args__ = (UniqueConstraint("order_id", "reference", name="uq_order_receipt_reference"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False)
    reference: Mapped[str] = mapped_column(String(120), nullable=False)
    received_by: Mapped[str] = mapped_column(String(120), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    lines: Mapped[list["PurchaseReceiptLineRecord"]] = relationship(cascade="all, delete-orphan", order_by="PurchaseReceiptLineRecord.id")


class PurchaseReceiptLineRecord(BaseModel):
    __tablename__ = "purchase_receipt_lines"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_receipt_quantity_positive"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(ForeignKey("purchase_receipts.id"), nullable=False)
    order_line_id: Mapped[str] = mapped_column(ForeignKey("purchase_order_lines.id"), nullable=False)
    product_sku: Mapped[str] = mapped_column(ForeignKey("products.sku"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class StockMovementRecord(BaseModel):
    __tablename__ = "stock_movements"
    __table_args__ = (CheckConstraint("(receipt_line_id IS NOT NULL) <> (issue_line_id IS NOT NULL)", name="ck_stock_movement_source"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    product_sku: Mapped[str] = mapped_column(ForeignKey("products.sku"), nullable=False)
    quantity_change: Mapped[int] = mapped_column(Integer, nullable=False)
    receipt_line_id: Mapped[str | None] = mapped_column(ForeignKey("purchase_receipt_lines.id"), unique=True, nullable=True)
    issue_line_id: Mapped[str | None] = mapped_column(ForeignKey("stock_issue_lines.id"), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    @property
    def movement_type(self) -> str:
        return "receipt" if self.receipt_line_id else "issue"


class StockIssueRecord(BaseModel):
    __tablename__ = "stock_issues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    reference: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    lines: Mapped[list["StockIssueLineRecord"]] = relationship(cascade="all, delete-orphan")


class StockIssueLineRecord(BaseModel):
    __tablename__ = "stock_issue_lines"
    __table_args__ = (UniqueConstraint("issue_id", "product_sku", name="uq_issue_product"), CheckConstraint("quantity > 0", name="ck_issue_quantity_positive"))

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    issue_id: Mapped[str] = mapped_column(ForeignKey("stock_issues.id"), nullable=False)
    product_sku: Mapped[str] = mapped_column(ForeignKey("products.sku"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class PurchaseOrderEventRecord(BaseModel):
    __tablename__ = "purchase_order_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False)
    event: Mapped[str] = mapped_column(String(32), nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
