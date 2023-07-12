from typing import Annotated

from aiodynamo.client import Table
from fastapi import APIRouter, Depends

from guardian.dependencies import dynamodb_table

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "UP"}


@router.post("/table")
async def post_table(table: Annotated[Table, Depends(dynamodb_table)]):
    return {"table": table.name, "exists": await table.exists()}
