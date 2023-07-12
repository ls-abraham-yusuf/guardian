from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiodynamo.client import Client, Table
from aiodynamo.credentials import Credentials
from aiodynamo.http.httpx import HTTPX
from httpx import AsyncClient
from structlog import get_logger
from yarl import URL

log = get_logger()


@asynccontextmanager
async def dynamodb_client(
    region: str, endpoint: URL, credentials: Credentials = Credentials.auto()
) -> AsyncGenerator[Client, None]:
    async with AsyncClient() as http:
        yield Client(
            http=HTTPX(http),
            credentials=credentials,
            region=region,
            endpoint=endpoint,
        )


async def ensure_table_exists(table: Table, schema: dict):
    if await table.exists():
        return

    log.warn(f"DynamoDB table {table.name!r} does not exist, creating it")

    await table.create(**schema)

    log.info(f"Successfully created DynamoDB table {table.name!r}.")
