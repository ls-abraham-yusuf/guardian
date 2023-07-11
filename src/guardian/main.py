from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from ls_logging import setup_logging
from structlog import get_logger

from guardian.config import guardian
from guardian.dependencies import create_dynamodb_table
from guardian.middleware import register_middlewares
from guardian.routers import auth, health

log = get_logger()

app = FastAPI(title="guardian")
app.mount("/static", StaticFiles(directory=guardian.server.STATIC_FILES_DIR), name="static")

register_middlewares(app, guardian)


@app.on_event("startup")
async def startup_event(_: Annotated[None, Depends(create_dynamodb_table)]):
    setup_logging(guardian.logging)
    log.info(f"Initializing API on port {guardian.server.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down API")


# Register your routers here
app.include_router(health.router, prefix="/management")
app.include_router(auth.router, prefix="/oauth", tags=["OAuth2"])
