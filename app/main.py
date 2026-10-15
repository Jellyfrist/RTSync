from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import router as auth_router, authorized_user, SESSION_COOKIE
from app.authorization import can_access_api

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
            """Check Google session + chapter-10 role before running business APIs."""
            path = request.url.path
            prefix = config.api_prefix.rstrip("/")
            public_gets = {
                f"{prefix}/health",
                f"{prefix}/auth/status",
                f"{prefix}/auth/google",
                f"{prefix}/auth/callback",
                f"{prefix}/auth/me",
            }
            if request.method == "OPTIONS":
                return await call_next(request)
            if request.method == "GET" and path in public_gets:
                return await call_next(request)
            if request.method == "POST" and path == f"{prefix}/auth/logout":
                return await call_next(request)

            try:
                user = await authorized_user(request.cookies.get(SESSION_COOKIE))
            except HTTPException as exc:
                return JSONResponse(
                    {"detail": exc.detail},
                    status_code=exc.status_code,
                    headers={"Cache-Control": "no-store"},
                )

            if not can_access_api(
                user["role"], request.method, path, prefix
            ):
                return JSONResponse(
                    {"detail": "บัญชีนี้ไม่มีสิทธิ์เข้าถึงฟังก์ชันดังกล่าว"},
                    status_code=403,
                    headers={"Cache-Control": "no-store"},
                )
            return await call_next(request)

    return application


app = create_app()
