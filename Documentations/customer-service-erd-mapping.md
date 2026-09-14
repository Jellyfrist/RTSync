# ERD & Data Mapping: Customer / Sales / Installation / After-sales

เอกสารนี้ออกแบบจาก workflow ที่แสดงใน UI ของ RT Sync Solar Workbench และครอบคลุม 5 ความสามารถหลัก:

1. ขายสินค้าและออกใบเสนอราคา/คำสั่งขาย
2. นัดหมายและติดตามงานติดตั้ง
3. แจ้งเตือนสินค้าเมื่อ Stock ต่ำกว่าหรือเท่ากับ Reorder Point
4. บริการหลังการขายและประวัติการบริการ
5. โปรไฟล์ลูกค้าแบบ master-detail ที่เชื่อมทุกกิจกรรมเข้าด้วยกัน

สำหรับหน้า Supplier โดยเฉพาะ รองรับการเพิ่ม/แก้ไขข้อมูล Supplier และการผูก SKU ว่าสินค้าแต่ละรายการซื้อจาก Supplier รายใด

## ERD (logical model)

```mermaid
erDiagram
    CUSTOMER ||--o{ CUSTOMER_SITE : owns
    CUSTOMER ||--o{ SALES_ORDER : places
    CUSTOMER ||--o{ SERVICE_TICKET : raises
    CUSTOMER_SITE ||--o{ INSTALLATION_JOB : hosts
    SALES_ORDER ||--o{ SALES_ORDER_ITEM : contains
    PRODUCT ||--o{ SALES_ORDER_ITEM : sold_as
    PRODUCT ||--o{ STOCK_MOVEMENT : tracks
    PRODUCT ||--o{ REORDER_ALERT : triggers
    SUPPLIER ||--o{ PRODUCT : supplies
    INSTALLATION_JOB }o--o| SALES_ORDER : fulfills
    INSTALLATION_JOB }o--o| EMPLOYEE : assigned_to
    SERVICE_TICKET }o--o| EMPLOYEE : owned_by
    INSTALLATION_JOB ||--o{ SERVICE_HISTORY : creates
    SERVICE_TICKET ||--o{ SERVICE_HISTORY : resolves_as
    CUSTOMER ||--o{ NOTIFICATION : receives
    PRODUCT ||--o{ NOTIFICATION : about
    INSTALLATION_JOB ||--o{ NOTIFICATION : about
    SERVICE_TICKET ||--o{ NOTIFICATION : about

    CUSTOMER {
      string customer_id PK
      string customer_code UK
      string name
      string phone
      string customer_type
      string account_status
      datetime created_at
    }
    CUSTOMER_SITE {
      string site_id PK
      string customer_id FK
      string address
      decimal latitude
      decimal longitude
      string site_status
    }
    PRODUCT {
      string product_id PK
      string sku UK
      string supplier_id FK
      string name
      string category
      int stock_qty
      int reorder_point
      string unit
      decimal unit_price
      string status
    }
    SUPPLIER {
      string supplier_id PK
      string name
      string category
      string delivery_lead_time
      string contact_phone
    }
    SALES_ORDER {
      string order_id PK
      string customer_id FK
      string order_no UK
      string status
      decimal subtotal
      decimal total_amount
      datetime ordered_at
    }
    SALES_ORDER_ITEM {
      string order_item_id PK
      string order_id FK
      string product_id FK
      int quantity
      decimal unit_price
      decimal line_total
    }
    INSTALLATION_JOB {
      string installation_id PK
      string order_id FK
      string site_id FK
      string assigned_employee_id FK
      date scheduled_date
      string time_slot
      string job_type
      string status
    }
    SERVICE_TICKET {
      string ticket_id PK
      string customer_id FK
      string assigned_employee_id FK
      string subject
      string priority
      string status
      datetime opened_at
      datetime closed_at
    }
    SERVICE_HISTORY {
      string history_id PK
      string customer_id FK
      string installation_id FK
      string ticket_id FK
      string service_type
      string detail
      string status
      datetime serviced_at
    }
    STOCK_MOVEMENT {
      string movement_id PK
      string product_id FK
      string reference_type
      string reference_id
      string movement_type
      int quantity
      int balance_after
      datetime occurred_at
    }
    REORDER_ALERT {
      string alert_id PK
      string product_id FK
      int stock_qty
      int reorder_point
      string status
      datetime created_at
      datetime resolved_at
    }
    EMPLOYEE {
      string employee_id PK
      string name
      string role
      string phone
      string employment_status
    }
    NOTIFICATION {
      string notification_id PK
      string customer_id FK
      string product_id FK
      string installation_id FK
      string ticket_id FK
      string notification_type
      string title
      string status
      datetime created_at
      datetime read_at
    }
```

## UI-to-data mapping

| UI surface / feature | Primary entities | Fields used | Key behavior |
| --- | --- | --- | --- |
| `/customers` customer list | `CUSTOMER`, `CUSTOMER_SITE` | `customer_code`, `name`, `phone`, `customer_type`, `account_status`, `address` | Filter by customer type/status; select one customer to show detail |
| `/suppliers` supplier directory | `SUPPLIER`, `PRODUCT` | `supplier_id`, `name`, `category`, `description`, `delivery_lead_time`, `sku_count`, `PRODUCT.supplier_id` | Add/edit Supplier; select Supplier to see all purchased SKUs; bind an existing product to the selected Supplier |
| Customer detail / service history | `CUSTOMER`, `SERVICE_HISTORY`, `INSTALLATION_JOB`, `SERVICE_TICKET` | `system`, `service_type`, `detail`, `serviced_at`, `status` | Timeline combines installation and after-sales activities |
| Sales tab | `SALES_ORDER`, `SALES_ORDER_ITEM`, `PRODUCT` | `order_no`, `customer_id`, `sku`, `quantity`, `unit_price`, `line_total`, `total_amount` | Add catalog items to draft quote; save order; preserve customer context |
| Installation appointment tab | `INSTALLATION_JOB`, `CUSTOMER_SITE`, `EMPLOYEE`, `SALES_ORDER` | `scheduled_date`, `time_slot`, `crew`, `job_type`, `status` | Create appointment and move status: awaiting confirmation → confirmed → preparing equipment → installing → completed |
| After-sales tab | `SERVICE_TICKET`, `SERVICE_HISTORY`, `EMPLOYEE`, `CUSTOMER` | `subject`, `priority`, `owner`, `status`, `opened_at`, `closed_at` | Open ticket, assign owner, track work, close ticket and append history |
| Inventory product table | `PRODUCT`, `SUPPLIER`, `STOCK_MOVEMENT` | `sku`, `name`, `category`, `stock_qty`, `unit`, `unit_price`, `supplier_id` | Register/edit product; receive stock; maintain movement ledger |
| Reorder Point tab | `PRODUCT`, `REORDER_ALERT`, `SUPPLIER` | `stock_qty`, `reorder_point`, `status`, `supplier_id` | Alert when `stock_qty <= reorder_point`; create purchasing request |
| Header notification panel | `NOTIFICATION` plus source entity | `notification_type`, `title`, `status`, `created_at`, source FK | Show low stock, unconfirmed appointments, and new service tickets |

## Existing API alignment

The current backend schemas are a starting point and map as follows:

| Existing schema | ERD entity | Notes |
| --- | --- | --- |
| `Customer` | `CUSTOMER` | Add `customer_code` uniqueness and `created_at` when persistence is introduced |
| `Product` | `PRODUCT` | Add `reorder_point`, `unit`, `supplier_id`, and `status` to support the inventory UI and supplier binding |
| `Supplier` | `SUPPLIER` | Existing `delivery` maps to `delivery_lead_time`; add `description`, contact fields, and a product relation later |
| `Employee` | `EMPLOYEE` | Existing payroll fields remain in employee/payroll domain; installation/service uses the same employee key |
| `CatalogSummary` | Read model / dashboard projection | Should be computed from `PRODUCT` and `STOCK_MOVEMENT`, not hard-coded |

## Recommended constraints and rules

- `customer_code`, `sku`, `order_no`, and `ticket_id` must be unique.
- `SALES_ORDER_ITEM.line_total = quantity * unit_price`; `SALES_ORDER.total_amount` is the sum of line totals plus any tax/discount policy.
- Stock changes must create a `STOCK_MOVEMENT`; do not update `PRODUCT.stock_qty` without an auditable reference.
- Create or keep one active `REORDER_ALERT` per product while `stock_qty <= reorder_point`; resolve it after stock rises above the point.
- An `INSTALLATION_JOB` should reference a `CUSTOMER_SITE`, even when a customer has only one site today.
- Closing a `SERVICE_TICKET` should write one `SERVICE_HISTORY` record and store `closed_at`.
- Notifications should be generated from domain events and marked read independently from the source record.

## Suggested implementation sequence

1. Extend Pydantic schemas and repositories with the entities/fields above.
2. Add REST resources for orders, order items, installation jobs, service tickets, stock movements, and notifications.
3. Replace mock arrays in the Vue views with API composables while retaining the current optimistic UI feedback.
4. Add database indexes on `customer_id`, `status`, `scheduled_date`, `product_id`, and `created_at`.
