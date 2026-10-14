from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, settings
from app.controllers import catalog, compat, customers, employees, health, procurement, suppliers


def create_app(config: Settings | None = None) -> FastAPI:
    """Build an isolated application for serving, tests or alternate configuration."""
    config = config if config is not None else settings
    application = FastAPI(title=config.app_name, version="0.1.0")
    allowed_origins = {
        config.frontend_origin.rstrip("/"),
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    }
    application.add_middleware(
        CORSMiddleware,
        allow_origins=sorted(allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for controller in (health, catalog, customers, suppliers, employees, procurement, compat):
        application.include_router(controller.router, prefix=config.api_prefix)

    # The deployed site deliberately has no login screen. Until genuine
    # authorization exists, serve only health checks: anonymous visitors must
    # never read or modify live business data even if DATABASE_URL gets added.
    if config.app_env.lower() == "production" and config.public_demo_mode:
        @application.middleware("http")
        async def protect_business_data(request: Request, call_next):
            health_path = f"{config.api_prefix.rstrip('/')}/health"
            if request.method == "GET" and request.url.path == health_path:
                return await call_next(request)
            return JSONResponse(
                status_code=503,
                content={"detail": "RTSync public demo: live database API is disabled until secure access control is implemented."},
                headers={"Cache-Control": "no-store"},
            )
    return application


app = create_app()
