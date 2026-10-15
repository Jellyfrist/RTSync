"""RTSync role permissions matching Chapter 10 actors and existing use cases.

UC-01 (payroll) and UC-02 (supplier management): Store owner only.
UC-03 (inventory), UC-04 (customers), UC-05 (sales/install/service),
UC-06 (fuel claims): Store owner and Staff.

The inventory use cases UC-03-02/03 include linking products with a supplier;
UC-03-06/07 create purchase orders in generic operations; UC-03-08 links
to supplier registration from the product form. These explicit workflow
dependencies are allowed without granting Staff the owner-only management
page /suppliers, employee/payroll records, or dedicated procurement APIs.
"""
from urllib.parse import unquote

OWNER = "owner"
EMPLOYEE = "employee"

EMPLOYEE_PAGES = frozenset({
    "/inventory", "/customers", "/sales",
    "/installations", "/service", "/fuel-claims",
})
OWNER_ONLY_PAGES = frozenset({"/payroll", "/suppliers"})

# Generic operations are not equivalent to the separate procurement database
# workflow. Limit access to collections represented in Chapter 10.
DAILY_OPERATIONS = frozenset({
    "sales", "quotations", "appointments", "serviceTickets", "fuelClaims",
})


def role_for_email(email: str, owner_emails: str, employee_emails: str) -> str | None:
    value = (email or "").strip().casefold()
    owners = {i.strip().casefold() for i in owner_emails.split(",") if i.strip()}
    employees = {i.strip().casefold() for i in employee_emails.split(",") if i.strip()}
    if not value:
        return None
    if value in owners:
        return OWNER
    if value in employees:
        return EMPLOYEE
    return None


def can_access_page(role: str, path: str) -> bool:
    path = path.split("?")[0].rstrip("/") or "/"
    if role == OWNER:
        return path in EMPLOYEE_PAGES | OWNER_ONLY_PAGES
    if role == EMPLOYEE:
        return path in EMPLOYEE_PAGES
    return False


def can_access_api(role: str, method: str, path: str, prefix: str = "/api") -> bool:
    """Fail-closed for Staff; never trust client-provided roles or collection."""
    if role == OWNER:
        return True
    if role != EMPLOYEE:
        return False

    prefix = prefix.rstrip("/")
    if not path.startswith(prefix + "/"):
        return False
    resource = unquote(path[len(prefix):]).rstrip("/")
    method = method.upper()
    segments = resource.lstrip("/").split("/")

    # UC-03: inventory, categories, stock receiving and item-supplier linking.
    if segments == ["inventory", "products"]:
        return method in {"GET", "POST"}
    if segments == ["inventory", "categories"]:
        return method in {"GET", "POST"}
    if segments == ["inventory", "summary"]:
        return method == "GET"
    if len(segments) == 3 and segments[:2] == ["inventory", "products"]:
        return method == "PUT"
    if len(segments) == 4 and segments[:2] == ["inventory", "products"] and segments[3] == "receive":
        return method == "POST"

    # Staff can select existing suppliers inside the inventory form.
    if resource == "/suppliers":
        # UC-03-08: registration from inventory uses the existing POST /suppliers.
        # The /suppliers management screen itself stays owner-only.
        return method in {"GET", "POST"}
    if (len(segments) == 4 and segments[0] == "suppliers"
            and segments[2] == "products"):
        return method in {"POST", "DELETE"}

    # UC-04: customer data, status and history.
    if resource == "/customers":
        return method in {"GET", "POST"}
    if len(segments) == 2 and segments[0] == "customers":
        return method == "PATCH"

    # Product lookup used by UC-05 sales/quotation screens.
    if resource in {"/catalog/products", "/catalog/summary"}:
        return method == "GET"

    # UC-03-06/07: Staff can create purchase request from Inventory.
    # UC-02-07: viewing/managing all supplier PO statuses is owner-only.
    if len(segments) == 2 and segments == ["operations", "purchaseOrders"]:
        return method == "POST"

    # UC-04/05/06: business operations (including fuel claim status changes).
    if (len(segments) == 2 and segments[0] == "operations"
            and segments[1] in DAILY_OPERATIONS):
        return method in {"GET", "POST"}
    if (len(segments) == 3 and segments[0] == "operations"
            and segments[1] in DAILY_OPERATIONS):
        return method == "PATCH"

    return False
