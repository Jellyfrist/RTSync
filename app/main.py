from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, settings
from app.controllers import catalog, customers, employees, health, procurement, suppliers


def create_app(config: Settings | None = None) -> FastAPI:
    """Build an isolated application for serving, tests or alternate configuration."""
    config = config if config is not None else settings
    application = FastAPI(title=config.app_name, version="0.1.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list({config.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"}),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for controller in (health, catalog, customers, suppliers, employees, procurement):
        application.include_router(controller.router, prefix=config.api_prefix)
    return application


app = create_app()
