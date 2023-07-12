from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from ls_logging import setup_logging
from structlog import get_logger

from guardian.config import guardian
from guardian.middleware import register_middlewares
from guardian.routers import auth, health

log = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(guardian.logging)

    log.info(f"Initializing API on port {guardian.server.PORT}")
    app.mount("/static", StaticFiles(directory=guardian.server.STATIC_FILES_DIR), name="static")

    register_middlewares(app, guardian)

    # Register your routers here
    app.include_router(health.router, prefix="/management")
    app.include_router(auth.router, prefix="/oauth", tags=["OAuth2"])

    yield

    log.info("Shutting down API")


app = FastAPI(title="guardian", lifespan=lifespan)
