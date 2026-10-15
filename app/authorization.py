"""Role-based authorization for existing RTSync pages and REST endpoints.

Only two application roles are supported: owner and employee.
Employee access is restricted to day-to-day operations; unknown endpoints fail
closed rather than inheriting access from a generic /operations handler.
"""
from urllib.parse import unquote


def _emails(value: str) -> set[str]:
    return {item.strip().casefold() for item in value.split(",") if item.strip()}


def role_for_email(email: str, *, owner_emails: str, employee_emails: str) -> str | None:
    normalized = (email or "").strip().casefold()
    if not normalized:
        return None
    if normalized in _emails(owner_emails):
        return "owner"
    if normalized in _emails(employee_emails):
        return "employee"
    return None


def is_allowed(role: str, method: str, path: str, api_prefix: str = "/api") -> bool:
    if role == "owner":
        return True
    if role != "employee":
        return False

    prefix = api_prefix.rstrip("/")
    if not path.startswith(prefix + "/"):
        return False
    resource = unquote(path[len(prefix):]).rstrip("/")
    method = method.upper()

    if resource in ("/inventory/products", "/inventory/categories", "/inventory/summary", "/catalog/products", "/catalog/summary", "/suppliers"):
        return method == "GET"

    # In-store customer operations, but never supplier edits or payroll APIs.
    if resource == "/customers":
        return method in {"GET", "POST"}
    if resource.startswith("/customers/") and method == "PATCH":
        return True
    if resource == "/inventory/products" and method == "POST":
        return False
    if resource.startswith("/inventory/products/"):
        if resource.endswith("/receive"):
            return method == "POST"
        return False
    if resource.startswith("/catalog/stock-issues"):
        return method == "POST" and resource == "/catalog/stock-issues"

    # Generic collection routes are explicitly scoped to allowed workflows.
    # fuelClaims: employees cannot access until claims are linked to auth.user.id
    # and can be filtered/updated by owner identity at the database level.
    parts = resource.strip("/").split("/")
    permitted_collections = {"sales", "quotations", "appointments", "serviceTickets"}
    if len(parts) == 2 and parts[0] == "operations":
        return parts[1] in permitted_collections and method in {"GET", "POST"}
    if len(parts) == 3 and parts[0] == "operations":
        return parts[1] in permitted_collections and method == "PATCH"
    return False
