from datetime import datetime

from pydantic import BaseModel, Field


class OrderLineInput(BaseModel):
    product_sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(gt=0)


class CreateOrderInput(BaseModel):
    supplier_id: str = Field(min_length=1, max_length=64)
    actor: str = Field(min_length=1, max_length=120)
    lines: list[OrderLineInput] = Field(min_length=1)


class ActorInput(BaseModel):
    actor: str = Field(min_length=1, max_length=120)


class ReceiptLineInput(BaseModel):
    order_line_id: str = Field(min_length=1)
    quantity: int = Field(gt=0)


class ReceiveOrderInput(ActorInput):
    reference: str = Field(min_length=1, max_length=120)
    lines: list[ReceiptLineInput] = Field(min_length=1)


class OrderLineOutput(BaseModel):
    id: str
    product_sku: str
    ordered_quantity: int
    received_quantity: int


class OrderOutput(BaseModel):
    id: str
    supplier_id: str
    status: str
    created_by: str
    created_at: datetime
    lines: list[OrderLineOutput]


class ReceiptLineOutput(BaseModel):
    order_line_id: str
    product_sku: str
    quantity: int


class ReceiptOutput(BaseModel):
    id: str
    order_id: str
    reference: str
    received_by: str
    received_at: datetime
    lines: list[ReceiptLineOutput]


class OrderEventOutput(BaseModel):
    event: str
    actor: str
    created_at: datetime


class StockMovementOutput(BaseModel):
    id: str
    product_sku: str
    quantity_change: int
    receipt_line_id: str | None
    issue_line_id: str | None
    movement_type: str
    created_at: datetime


class StockIssueLineInput(BaseModel):
    product_sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(gt=0)


class CreateStockIssueInput(BaseModel):
    reference: str = Field(min_length=1, max_length=120)
    actor: str = Field(min_length=1, max_length=120)
    lines: list[StockIssueLineInput] = Field(min_length=1)


class StockIssueLineOutput(BaseModel):
    product_sku: str
    quantity: int


class StockIssueOutput(BaseModel):
    id: str
    reference: str
    actor: str
    created_at: datetime
    lines: list[StockIssueLineOutput]
