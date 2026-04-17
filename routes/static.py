from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(tags=["static"])


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(
        Path(__file__).parent.parent / "static/favicon/favicon.ico",
        media_type="image/x-icon",
    )
