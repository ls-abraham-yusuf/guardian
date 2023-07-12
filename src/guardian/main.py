from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from ls_logging import setup_logging
from structlog import get_logger

from guardian.config import guardian
from guardian.middleware import RedisMiddleware, SessionMiddleware
from guardian.routers import auth, health

log = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(guardian.logging)

    log.info(f"Initializing API on port {guardian.server.PORT}")
    app.mount("/static", StaticFiles(directory=guardian.server.STATIC_FILES_DIR), name="static")

    # Register your routers here
    app.include_router(health.router, prefix="/management")
    app.include_router(auth.router, prefix="/oauth", tags=["OAuth2"])

    yield

    log.info("Shutting down API")


app = FastAPI(title="guardian", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=guardian.server.SECRET_KEY,
    session_cookie=guardian.server.SESSION_COOKIE_NAME,
    same_site="none",
    https_only=False,
)
app.add_middleware(RedisMiddleware, url=guardian.redis.uri)
