from typing import AsyncGenerator

from aiodynamo.client import Table
from structlog import get_logger

from guardian.config import guardian
from guardian.database import SCHEMA, dynamodb_client, ensure_table_exists

log = get_logger()


async def dynamodb_table() -> AsyncGenerator[Table, None]:
    async with dynamodb_client(guardian.dynamodb.REGION, guardian.dynamodb.endpoint) as client:
        table = client.table(guardian.dynamodb.TABLE_NAME)

        await ensure_table_exists(table, SCHEMA)

        yield table
