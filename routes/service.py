from fastapi import APIRouter
from core.api_client import get_cdn


router = APIRouter(
    prefix="/service",
    tags=["service"],
)


@router.get("/thumb_servers", response_model=list[str])
async def thumb_servers():
    data = await get_cdn()
    return data["thumb_servers"]
