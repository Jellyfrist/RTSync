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
`/api` (not the old domain). For the no-login public demo, keep
`VITE_USE_MOCK=true` so the UI displays local sample records and does not
claim to show or persist Supabase data.

## Environment variables

Configure all variables on the **single Vercel project `rt-sync`**:

| Name | Where | Value |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Vite build | `/api` |
| `VITE_USE_MOCK` | Vite build | `true` (public demo sample data) |
| `PUBLIC_DEMO_MODE` | Python service | `true` (production API access guard) |
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

## Public no-login demo and database safety

The owner requested **no login whatsoever**. Visitors can open the Vue site
without Vercel or in-app login, but this is **a public demonstration** — not
an anonymous full-access production database application.

- `APP_ENV=production` and `PUBLIC_DEMO_MODE=true` cause the FastAPI
  middleware to allow only `GET /api/health`. All other API paths,
  including creates/updates/deletes and `/docs`, return 503 with no-store.
  The middleware is designed to fail closed for a production demo by default
  even if `DATABASE_URL` is configured. Never set
  `PUBLIC_DEMO_MODE=false` on a public deployment while routes lack
  authentication/authorization.
- `VITE_USE_MOCK=true` enables local browser-side sample-data fallback.
  It is **not live Supabase data**; a banner tells visitors that changes
  are not saved to Supabase.
- The UI previously contained an invented `SUPER ADMIN` user/logout
  control; production demo mode replaces it with a demo label.

**Critical Supabase issue:** 26 `public` tables have RLS disabled and the
Supabase `anon` and `authenticated` roles have broad privileges.
Avoid exposing Supabase API keys in the browser until database grants/RLS
are reviewed. RLS changes must be planned and reviewed with the owner,
as enabling RLS without policies can break existing apps. For a future
live-data deployment, implement safe access controls or an explicitly
designed and isolated anonymous demo data model before unblocking APIs.

## Verify public deployment

1. Check Production is **READY** under the Vercel `rt-sync` project.
2. Confirm `https://rt-sync.vercel.app` and `/inventory` load without login.
3. Check `GET /api/health` returns `{"status":"ok"}`.
4. Check `GET /api/inventory/products` and `POST /api/inventory/products`
   return **503** (no anonymous business-data access).
5. Confirm the visible demo banner and no login/logout controls.
6. Keep real Supabase data untouched. Do not run migrations during deploy.

The old `rtsync-web` and `rtsync-api` domains are not needed when
the unified project is validated. Keep any legacy project as a
rollback option until the unified deployment is proven healthy.
