from dataclasses import dataclass, field
from pathlib import Path

from ls_logging import LoggingSettings
from pydantic import BaseSettings
from yarl import URL


class ServerSettings(BaseSettings):
    PORT: int = 8080
    ENABLE_RELOAD: bool = False
    SECRET_KEY: str = "secret"
    SESSION_COOKIE_NAME: str = "SESSION"
    STATIC_FILES_DIR: Path = Path(__file__).parent / "static"
    JINJA2_TEMPLATES_DIR: Path = Path(__file__).parent / "templates"

    class Config:
        env_prefix = "SERVER_"


class DynamoDBSettings(BaseSettings):
    HOST: str = "http://dynamodb"
    PORT: str = "8000"
    REGION: str = "eu-central-1"
    TABLE_NAME: str = "openid"

    class Config:
        env_prefix = "DYNAMO_"

    @property
    def endpoint(self) -> URL:
        return URL(f"{self.HOST}:{self.PORT}")


class RedisSettings(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 6379
    USER: str = "default"
    PASSWORD: str = ""
    USE_SSL: bool = False
    DATABASE: int = 0

    class Config:
        env_prefix = "REDIS_"

    @property
    def uri(self):
        scheme = "rediss" if self.USE_SSL else "redis"
        return (
            f"{scheme}://{self.USER}:{self.PASSWORD}"  # pragma: allowlist secret
            f"@{self.HOST}:{self.PORT}/{self.DATABASE}"
        )


@dataclass
class Guardian:
    dynamodb: DynamoDBSettings = field(default_factory=DynamoDBSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    redis: RedisSettings = field(default_factory=RedisSettings)
    server: ServerSettings = field(default_factory=ServerSettings)


guardian = Guardian()
