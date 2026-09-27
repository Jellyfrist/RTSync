# RT Sync

Vue 3 frontend and FastAPI backend organized around MVC, with reusable controllers, domain classes and replaceable repositories.

- [Architecture and extension guide](docs/architecture.md)
- [Backend setup and API](app/README.md)

Copy `.env.example` to `.env` at the repository root and set `DATABASE_URL` and `VITE_API_BASE_URL`. The backend and Vite both read this file. Keep database credentials out of variables prefixed with `VITE_`.

## Frontend

```bash
cd frontend
npm ci
npm run dev
```

The backend runs from the repository root using `app.main`. Procurement, inventory and outbound stock issue screens use the backend API. Customer and payroll screens still use demo data. Outbound issues record stock changes but do not create sales orders or installation schedules.

```bash
npm test
npm run build
```
