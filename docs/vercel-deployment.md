# Deploy RT Sync to Vercel

RT Sync consists of a Vue 3/Vite SPA (`frontend/`) and a FastAPI backend
(`app/`) that uses PostgreSQL (Supabase). Deploy **two Vercel projects**
from the **same GitHub repository** so they can have independent build
settings and environment variables.

> **Security warning:** The current FastAPI routes do not implement
> authentication or authorization. The backend includes customer/employee
> records and data-changing inventory, supplier and order endpoints.
> **Do not deploy with real customer, employee or business data to a public
> backend** until authentication and authorization are added. For a
> classroom/demo deployment, use an isolated database containing only
> non-sensitive sample data. Some frontend screens offer mock fallbacks,
> but mock mode does not replace the backend for all actions.

## 1. Prepare an isolated PostgreSQL database

1. Create a Supabase project (or use a separate demo database).
2. Copy the PostgreSQL connection string from your Supabase dashboard and
   make sure it uses the `postgresql+psycopg://` SQLAlchemy driver prefix.
   When deploying a serverless backend, use the Supabase pooler connection
   details appropriate for your project.
3. **Before deployment**, initialize the schema from your local machine
   (or a controlled CI/migration job):

   ```bash
   python -m pip install -r app/requirements.txt
   DATABASE_URL='postgresql+psycopg://...' python -m app.scripts.init_db
   ```

   `init_db` may alter tables and numeric columns in an existing database.
   Back up existing data first. Never run migrations automatically on
   every serverless request.

## 2. Deploy the FastAPI backend

At [vercel.com/new](https://vercel.com/new), import
`Jellyfrist/RTSync` and create a project named, for example,
`rtsync-api`.

- **Root Directory:** repository root (`./`; do not select `app/`).
- **Framework:** FastAPI / Python automatic detection.
- **Build Command / Output Directory:** leave the framework defaults.
- Entrypoint: `index.py` exports the existing `app.main:app` instance.
- Python dependencies: root `requirements.txt` points to
  `app/requirements.txt`.
- Python version: `.python-version` pins Python 3.12.

Configure these **backend** environment variables on Vercel:

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | Your demo Supabase PostgreSQL connection URI, using `postgresql+psycopg://` |
| `APP_ENV` | `production` |
| `APP_NAME` | `RT Sync API` (optional) |
| `API_PREFIX` | `/api` |
| `FRONTEND_ORIGIN` | Your **frontend** production URL without the trailing slash |

When the backend finishes deploying, verify:

- `https://<your-backend-domain>/api/health` returns `{"status":"ok"}`.
- `https://<your-backend-domain>/docs` displays the FastAPI API docs.

Do not put a Supabase database password or `DATABASE_URL` in any
`VITE_` variable.

## 3. Deploy the Vue frontend

Import the **same** `Jellyfrist/RTSync` repository again in Vercel
as a second project named, for example, `rtsync-web`.

- **Root Directory:** `frontend`.
- **Framework Preset:** Vite.
- **Install Command:** `npm ci`.
- **Build Command:** `npm run build`.
- **Output Directory:** `dist`.

Configure these **frontend** environment variables:

| Variable | Value |
| --- | --- |
| `VITE_API_BASE_URL` | `https://<your-backend-domain>/api` |
| `VITE_USE_MOCK` | `false` for backend integration; `true` only for an intentionally partial UI demo |

The `frontend/vercel.json` file rewrites deep links to
`/index.html`, allowing `/customers`, `/inventory`, etc. to work
when opened or refreshed directly.

## 4. Connect the deployed projects

1. Copy the production URL of the Vue frontend.
2. Set the backend project's `FRONTEND_ORIGIN` to that exact origin,
   for example `https://rtsync-web.vercel.app` (no trailing slash).
3. Redeploy the backend after updating the environment variable.
4. Confirm `VITE_API_BASE_URL` on the frontend ends in `/api` and
   redeploy the frontend if you changed it.
5. Visit the frontend and check API traffic in the browser Network tab.

Because the existing CORS configuration permits one configured frontend
origin (plus local development URLs), branch preview domains may need
separate CORS configuration.

## 5. Troubleshooting

- **Vue page returns 404 on refresh:** confirm the frontend Vercel
  project's root directory is `frontend`, so its `vercel.json`
  rewrite is applied.
- **Requests go to localhost in production:** set
  `VITE_API_BASE_URL` in the frontend project and redeploy. Vite embeds
  these values at **build** time.
- **CORS errors:** check `FRONTEND_ORIGIN` on the backend matches the
  frontend origin exactly, without a trailing slash, and redeploy.
- **API returns 500 / database error:** check `DATABASE_URL`, pooler
  network access, database credentials and whether `init_db` has run.
- **Backend import/build error:** ensure the backend project's root
  directory is the repository root, not `app/` or `frontend/`.

Production deployment should be considered incomplete until access
control, error monitoring, backups, and a versioned database migration
strategy are in place.
