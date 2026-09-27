from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import SessionDependency
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.schemas.procurement import (
    ActorInput, CreateOrderInput, OrderEventOutput, OrderLineOutput,
    OrderOutput, ReceiveOrderInput, ReceiptLineOutput, ReceiptOutput,
    StockMovementOutput,
)
from app.services.procurement_service import ProcurementService, WorkflowError

router = APIRouter(prefix="/purchase-orders", tags=["procurement"])


def get_service(session: SessionDependency) -> ProcurementService:
    return ProcurementService(PurchaseOrderRepository(session))


Service = Annotated[ProcurementService, Depends(get_service)]


def handle_error(error: WorkflowError) -> None:
    raise HTTPException(status_code=error.status_code, detail=error.message) from error


def order_output(order) -> OrderOutput:
    return OrderOutput(
        id=order.id, supplier_id=order.supplier_id, status=order.status,
        created_by=order.created_by, created_at=order.created_at,
        lines=[OrderLineOutput(id=line.id, product_sku=line.product_sku, ordered_quantity=line.ordered_quantity, received_quantity=line.received_quantity) for line in order.lines],
    )


def receipt_output(receipt) -> ReceiptOutput:
    return ReceiptOutput(
        id=receipt.id, order_id=receipt.order_id, reference=receipt.reference,
        received_by=receipt.received_by, received_at=receipt.received_at,
        lines=[ReceiptLineOutput(order_line_id=line.order_line_id, product_sku=line.product_sku, quantity=line.quantity) for line in receipt.lines],
    )


@router.get("", response_model=list[OrderOutput])
def list_orders(service: Service):
    return [order_output(order) for order in service.list_orders()]


@router.post("", status_code=201, response_model=OrderOutput)
def create_order(payload: CreateOrderInput, service: Service):
    try:
        return order_output(service.create(payload))
    except WorkflowError as error:
        handle_error(error)


@router.get("/{order_id}", response_model=OrderOutput)
def get_order(order_id: str, service: Service):
    try:
        return order_output(service.get_order(order_id))
    except WorkflowError as error:
        handle_error(error)


@router.post("/{order_id}/approve", response_model=OrderOutput)
def approve_order(order_id: str, payload: ActorInput, service: Service):
    try:
        return order_output(service.approve(order_id, payload.actor))
    except WorkflowError as error:
        handle_error(error)


@router.post("/{order_id}/receipts", status_code=201, response_model=ReceiptOutput)
def receive_order(order_id: str, payload: ReceiveOrderInput, service: Service):
    try:
        return receipt_output(service.receive(order_id, payload))
    except WorkflowError as error:
        handle_error(error)


@router.get("/{order_id}/history")
def order_history(order_id: str, service: Service):
    try:
        events, receipts = service.history(order_id)
    except WorkflowError as error:
        handle_error(error)
    return {
        "events": [OrderEventOutput(event=item.event, actor=item.actor, created_at=item.created_at) for item in events],
        "receipts": [receipt_output(item) for item in receipts],
    }
