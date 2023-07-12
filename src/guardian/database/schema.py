from aiodynamo.models import GlobalSecondaryIndex, KeySchema, KeySpec, KeyType, Projection, ProjectionType, Throughput


class Attributes:
    PK = "PK"
    SK = "SK"
    EntityId = "EntityId"
    EntityType = "EntityType"
    Username = "Username"
    ClientId = "ClientId"
    TokenId = "TokenId"


SCHEMA = {
    "throughput": Throughput(read=1, write=1),
    "keys": KeySchema(
        hash_key=KeySpec(
            name=Attributes.PK,
            type=KeyType.string,
        ),
        range_key=KeySpec(
            name=Attributes.SK,
            type=KeyType.string,
        ),
    ),
    "lsis": None,
    "gsis": [
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
    "stream": None,
    "wait_for_active": True,
}
