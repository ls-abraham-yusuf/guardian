from typing import Annotated, AsyncGenerator

from aiodynamo.client import Client
from aiodynamo.credentials import Credentials
from aiodynamo.http.httpx import HTTPX
from aiodynamo.models import GlobalSecondaryIndex, KeySchema, KeySpec, KeyType, Projection, ProjectionType, Throughput
from fastapi import Depends
from httpx import AsyncClient
from structlog import get_logger

from guardian.config import guardian

log = get_logger()


class Attributes:
    PK = "PK"
    SK = "SK"
    EntityId = "EntityId"
    EntityType = "EntityType"
    Username = "Username"
    ClientId = "ClientId"
    TokenId = "TokenId"


async def get_dynamodb_client() -> AsyncGenerator[Client, None]:
    async with AsyncClient() as http:
        yield Client(
            http=HTTPX(http),
            credentials=Credentials.auto(),
            region=guardian.dynamodb.REGION,
            endpoint=guardian.dynamodb.endpoint,
        )


async def create_dynamodb_table(client: Annotated[Client, Depends(get_dynamodb_client)]) -> None:
    table = client.table(guardian.dynamodb.TABLE_NAME)
    if await table.exists():
        return

    log.warn(f"DynamoDB table {table.name!r} does not exist, creating it")
    await table.create(
        throughput=Throughput(read=10, write=10),
        keys=KeySchema(
            hash_key=KeySpec(
                name=Attributes.PK,
                type=KeyType.string,
            ),
            range_key=KeySpec(
                name=Attributes.SK,
                type=KeyType.string,
            ),
        ),
        gsis=[
            GlobalSecondaryIndex(
                name=Attributes.SK + "Index",
                schema=KeySchema(
                    hash_key=KeySpec(
                        name=Attributes.SK,
                        type=KeyType.string,
                    ),
                    range_key=KeySpec(
                        name=Attributes.EntityType,
                        type=KeyType.string,
                    ),
                ),
                projection=Projection(
                    type=ProjectionType.keys_only,
                ),
                throughput=Throughput(read=1, write=1),
            ),
            GlobalSecondaryIndex(
                name=Attributes.EntityType + "Index",
                schema=KeySchema(
                    hash_key=KeySpec(
                        name=Attributes.EntityType,
                        type=KeyType.string,
                    ),
                    range_key=KeySpec(
                        name=Attributes.EntityId,
                        type=KeyType.string,
                    ),
                ),
                projection=Projection(
                    type=ProjectionType.keys_only,
                ),
                throughput=Throughput(read=1, write=1),
            ),
            GlobalSecondaryIndex(
                name=Attributes.Username + "Index",
                schema=KeySchema(
                    hash_key=KeySpec(
                        name=Attributes.Username,
                        type=KeyType.string,
                    ),
                    range_key=KeySpec(
                        name=Attributes.EntityType,
                        type=KeyType.string,
                    ),
                ),
                projection=Projection(
                    type=ProjectionType.keys_only,
                ),
                throughput=Throughput(read=1, write=1),
            ),
            GlobalSecondaryIndex(
                name=Attributes.ClientId + "Index",
                schema=KeySchema(
                    hash_key=KeySpec(
                        name=Attributes.ClientId,
                        type=KeyType.string,
                    ),
                    range_key=KeySpec(
                        name=Attributes.EntityType,
                        type=KeyType.string,
                    ),
                ),
                projection=Projection(
                    type=ProjectionType.keys_only,
                ),
                throughput=Throughput(read=1, write=1),
            ),
            GlobalSecondaryIndex(
                name=Attributes.TokenId + "Index",
                schema=KeySchema(
                    hash_key=KeySpec(
                        name=Attributes.TokenId,
                        type=KeyType.string,
                    ),
                    range_key=KeySpec(
                        name=Attributes.EntityType,
                        type=KeyType.string,
                    ),
                ),
                projection=Projection(
                    type=ProjectionType.keys_only,
                ),
                throughput=Throughput(read=1, write=1),
            ),
        ],
    )
    log.info(f"Successfully created DynamoDB table {table.name!r}.")
