from uvicorn import run

from guardian import config

run(
    "guardian.main:app",
    host="0.0.0.0",
    port=config.guardian.SERVER_PORT,
    reload=config.guardian.ENABLE_RELOAD,
    log_level=config.guardian.LOG_LEVEL,
    access_log=config.guardian.ENABLE_ACCESS_LOG,
)
