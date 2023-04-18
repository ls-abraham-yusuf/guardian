from logging import getLogger

from fastapi import FastAPI
from lssvc.logs import initialize_logging
from lssvc.management import Management
from structlog import get_logger

from guardian import config
from guardian.routers import example_router

log = get_logger()
app = FastAPI(title="guardian")
management = Management()


@app.on_event("startup")
async def startup_event():
    initialize_logging()
    log.info(f"Initializing API on port {config.guardian.SERVER_PORT}")

    # TODO: Quick fix for uvicorn logs, remove if fixed in `lssvc.logs`
    getLogger("uvicorn.access").disabled = not config.guardian.ENABLE_ACCESS_LOG


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down API")


# Register your routers here
app.include_router(management.get_router(), prefix="/management")
app.include_router(example_router.router, prefix="/example")  # TODO: Remove, only for dev purposes
