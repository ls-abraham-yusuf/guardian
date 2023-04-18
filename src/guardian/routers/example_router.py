import structlog
from fastapi import APIRouter
from starlette.requests import Request

router = APIRouter()

log = structlog.get_logger()


@router.post("/", tags=["Example route"])
async def get_body(request: Request):
    """
    Dummy Endpoint that receives any JSON document
    """
    return await request.json()
