from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.middleware import RequestContextMiddleware
from app.config.logging import configure_logging
from app.config.settings import get_settings

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(RequestContextMiddleware)
app.include_router(health_router)
