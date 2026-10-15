from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import router as auth_router, authorized_user, SESSION_COOKIE

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
    application.include_router(auth_router, prefix=config.api_prefix)

    if config.rtsync_auth_required:
        @application.middleware("http")
        async def enforce_google_auth(request: Request, call_next):
            # The callback/login and health check must be reachable without a session.
            # Documentation and all data routes remain protected.
            path = request.url.path
            public_routes = {
                f"{config.api_prefix}/health",
                f"{config.api_prefix}/auth/google",
                f"{config.api_prefix}/auth/callback",
                f"{config.api_prefix}/auth/me",
                f"{config.api_prefix}/auth/logout",
            }
            if request.method == "OPTIONS" or (request.method == "GET" and path in public_routes) or (path == f"{config.api_prefix}/auth/logout" and request.method == "POST"):
                return await call_next(request)
            try:
                await authorized_user(request.cookies.get(SESSION_COOKIE))
            except Exception as exc:
                # Keep HTTPException detail/status; do not expose internal data.
                from fastapi import HTTPException
                if isinstance(exc, HTTPException):
                    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers={"Cache-Control": "no-store"})
                raise
            return await call_next(request)
    return application


app = create_app()
