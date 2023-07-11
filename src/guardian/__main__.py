from uvicorn import run

from guardian.config import guardian

run(
    "guardian.main:app",
    host="0.0.0.0",
    port=guardian.server.PORT,
    reload=guardian.server.ENABLE_RELOAD,
    log_level=guardian.logging.level,
)
