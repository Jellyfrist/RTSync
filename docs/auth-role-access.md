# RTSync access control — implementation note (not a Use Case specification)

Source of actor scope: **RTSync Chapter 10 Use Case Diagram/Specification,
Iteration 1 (UC-01-00 to UC-06-00) and Iteration 2 (45 sub-features)**.
The chapter document and all original business use cases are unchanged.

## Actors and existing pages

| Existing UI module / route | Store owner | Staff |
| --- | --- | --- |
| UC-01: `/payroll` | Yes | No |
| UC-02: `/suppliers` | Yes | No (see UC-03-08 below) |
| UC-03: `/inventory` | Yes | Yes |
| UC-04: `/customers` | Yes | Yes |
| UC-05: `/sales`, `/installations`, `/service` | Yes | Yes |
| UC-06: `/fuel-claims` | Yes | Yes |

This is **module/actor access control**, not a new business feature:
`app/authorization.py` checks FastAPI API paths and methods, Vue Router
blocks unauthorized pages, and the sidebar hides owner-only modules.
The backend is authoritative and denies unknown actions for Staff.

### Required existing cross-module use cases

- UC-03-02/03: Staff may list existing suppliers and link/unlink a product
  to a supplier from the inventory module.
- UC-03-06/07: Staff may POST a Reorder Point/manual PO to
  `/api/operations/purchaseOrders`, but may not list/modify all PO statuses
  on the owner-only supplier management page (UC-02-07).
- UC-03-08: Staff may navigate to
  `/suppliers?from=inventory` only to create a supplier from the inventory
  form and return to Inventory. This is a restricted supplier-creation
  surface, not the owner-only supplier administration view; employees
  cannot change supplier categories or edit existing suppliers.
- UC-06-01 to UC-06-05: **both actors** may list/create/edit/change fuel-claim
  statuses, as specified. Do not silently add a per-employee ownership rule
  that does not exist in the document.

The dedicated backend `/api/purchase-orders` procurement workflow is
distinct from the `operations` collection `purchaseOrders` used by UI.
Do not grant new Staff rights to that dedicated workflow.

## Activation — requires owner configuration

The Google Auth and RBAC code is **opt-in**, with default
`RTSYNC_AUTH_REQUIRED=false`. Until activated, the existing Vercel
Authentication protects the deployment (it does not identify the app's
`owner` vs `employee` role).

To enable after testing, the project owner must:

1. In Supabase Auth for existing project `zbgomqxlqmcucekjccmt`, enable
   the **Google** provider using Google OAuth Client ID/Secret.
   The Google Cloud authorized redirect URI goes to the Supabase project
   Auth callback `https://zbgomqxlqmcucekjccmt.supabase.co/auth/v1/callback`.
   Add `https://rt-sync.vercel.app/api/auth/callback**` to Supabase's
   permitted redirect URLs (allows the state query); verify redirect URL
   matching with Supabase Auth settings.
2. In the **rt-sync Vercel project**, add server-only environment variables
   `RTSYNC_OWNER_EMAILS` and `RTSYNC_EMPLOYEE_EMAILS` as separate,
   comma-separated approved Google addresses. A store owner's address
   always takes precedence if accidentally listed in both.
   The preconfigured `SUPABASE_AUTH_KEY` is a backend-only *publishable*
   Supabase key; it is not a database password or service-role key.
3. Activate `RTSYNC_AUTH_REQUIRED=true`, deploy, verify Google Login
   inside the Vercel-protected project for one approved Owner and Staff
   account, then switch Vercel Deployment Protection off **only after**
   access checks and session/callback behavior are verified.
4. Verify `/api/auth/status`, `/api/auth/me`, role page redirects,
   Staff `GET /api/employees` returns 403 and Staff
   `PATCH /api/operations/fuelClaims/{id}` remains allowed after login
   (test safely, without modifying production records).

**Do not** expose `DATABASE_URL`, `SUPABASE_AUTH_KEY`, a service-role key,
or all-RLS-disabled Supabase tables in a browser build. The server uses a
protected PostgreSQL connection. Supabase's currently unrestricted table
grants/RLS require separate security review before public exposure of the
Supabase Data REST endpoints.

If the OAuth flow fails, leave Vercel Authentication enabled and
`RTSYNC_AUTH_REQUIRED=false`; never disable both guards.

## Testing

Run `python -m unittest app.tests.test_authorization` in an environment
with the project's FastAPI test dependencies installed. The tests cover
role mapping, permitted routes, blocked access and unknown generic
operations collections. Production deploy success alone is not proof of
OAuth or Supabase read/write correctness.
