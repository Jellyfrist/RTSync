# RT Sync — Unified Vercel Services Deployment

This repository runs **Vue 3 + Vite** and **FastAPI** in **one Vercel project**, via [Vercel Services](https://vercel.com/kb/guide/vercel-services).

- Production domain: https://rt-sync.vercel.app
- Vercel project: `rt-sync` (Vercel ID `prj_QvdauaWS8lwbnKjQKMb3azWlV4wX`)
- GitHub: `Jellyfrist/RTSync`
- Supabase: [RTSync database](https://supabase.com/dashboard/project/zbgomqxlqmcucekjccmt)
- Backend: `https://rt-sync.vercel.app/api/*`
- Frontend: `https://rt-sync.vercel.app/*`

## Project architecture

The root `vercel.json` defines two independently built services and orders
the public rewrites so that FastAPI's `/api/*` paths take priority over the
Vue catch-all. The Vite service at `frontend/` uses its existing SPA fallback
configuration for Vue Router. The Python service at repository root imports
`app.main:app` via `index.py`. The existing root `requirements.txt` and
`.python-version` enable Python deployment.

The frontend's API client defaults to **relative `/api`**, not an absolute
backend hostname. Requests stay same-origin, so cross-domain CORS is no longer
needed for the web app. If `VITE_API_BASE_URL` is set on Vercel, set it to
`/api` (not the old domain). Keep `VITE_USE_MOCK=false` so production errors
are not disguised by local demo data.

## Environment variables

Configure all variables on the **single Vercel project `rt-sync`**:

| Name | Where | Value |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Vite build | `/api` |
| `VITE_USE_MOCK` | Vite build | `false` |
| `APP_ENV` | Python service | `production` |
| `API_PREFIX` | Python service | `/api` |
| `FRONTEND_ORIGIN` | Python service | `https://rt-sync.vercel.app` |
| `DATABASE_URL` | **Secret for Python only** | Existing Supabase PostgreSQL connection URI (Transaction Pooler, port 6543, scheme `postgresql+psycopg://`) |

**Do not commit, paste into frontend code, or prefix database credentials
with `VITE_`.** A Supabase project reference is NOT a database password.
The database password/URI must be obtained by the owner from the Supabase
**Connect → Transaction Pooler** page and saved as a sensitive/encrypted
environment variable in the Vercel project. Redeploy after changes.

The backend's SQLAlchemy engine disables Psycopg prepared statements on
transaction pooler connections, per Supabase's
[connection guide](https://supabase.com/docs/guides/database/connecting-to-postgres).

## Existing Supabase database — preserve data

Use only project ID `zbgomqxlqmcucekjccmt`. The database has 26 existing
`public` tables and business data, including inventory, purchasing, field
jobs, and invoices/quotes. **Never create another Supabase project, drop
tables, or run `python -m app.scripts.init_db` automatically from the
deployment pipeline.** The existing schema carries revisions in
`public.schema_migrations`. Back up the database and review changes before
any new schema migration.

## Security requirements before public use

**The single Vercel project must retain Vercel Authentication protection
(`ssoProtection: all`) until a proper application login and authorization
system is built and tested.** The current navigation header previously used
a hard-coded `SUPER ADMIN` label; this is not proof of a logged-in user.
The FastAPI routes do not yet authenticate users or check business roles.

**Critical Supabase security risk:** 26 tables have RLS disabled and the
Supabase `anon` and `authenticated` roles have broad table privileges.
Do **not** expose a Supabase publishable/anon key to the browser while this
is unresolved. The database must have appropriate grants/RLS and the
application must enforce real user authentication and authorization
before lifting deployment protection. Design and verify the RLS policy
per business role before applying it; enabling RLS without policies can
break existing applications. Never automatically change live RLS grants
or existing data without review.

Keep `DATABASE_URL` secret, enable database backups, monitor errors, and
use least-privilege credentials in production. Deployment readiness does
not mean authentication or database access is working.

## Verify (after setting the secret)

1. Check Vercel deployment is **READY** and project framework is **Services**.
2. Open `https://rt-sync.vercel.app/` when signed into an authorized Vercel account.
3. Check `https://rt-sync.vercel.app/api/health` is `{"status":"ok"}`.
4. Check a Vue deep link, e.g. `/inventory`, refreshes successfully.
5. After `DATABASE_URL` is set, test **read-only** `/api/inventory/products`
   against the existing Supabase records behind Vercel Authentication.
6. Test a representative write only after explicit approval, with a
   reversible test record, and verify it appears in PostgreSQL.

The old `rtsync-web` and `rtsync-api` domains are not needed when
the unified project is validated. Keep any legacy project as a
rollback option until the unified deployment is proven healthy.
