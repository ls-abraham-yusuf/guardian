from lssvc.config import ApiServiceSettings, LogSettings


class Guardian(ApiServiceSettings, LogSettings):
    # enables auto-reload based on uvicorn
    ENABLE_RELOAD: bool = False

    # base log level for all loggers
    LOG_LEVEL: str = "INFO".lower()

    # enabling access logs
    ENABLE_ACCESS_LOG: bool = True

    # formats json longs into multiple lines
    ENABLE_PRETTY_JSON_LOGS: bool = False

    # enable non json logs
    ENABLE_DEV_LOGS: bool = False

    # log kafka messages in case processing fails, used in lower envs, only applies to RetryingConsumer
    LOG_KAFKA_RECORDS: bool = False


guardian = Guardian()
