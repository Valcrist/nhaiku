import mimetypes
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from core.constants import COVER_DIR, THUMB_DIR, IMAGE_DIR
from toolbox.utils import get_env, debug


router = APIRouter(tags=["static"])

mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/avif", ".avif")


def _resolve_safe(base: Path | str, rel: str) -> Path:
    resolved = (Path(base) / rel).resolve()
    if not resolved.is_relative_to(Path(base).resolve()):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not resolved.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return resolved


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(
        Path(__file__).parent.parent / "static/favicon/favicon.ico",
        media_type="image/x-icon",
    )


@router.get("/cover/{path:path}")
async def cover(path: str):
    return FileResponse(_resolve_safe(COVER_DIR, path))


@router.get("/thumb/{path:path}")
async def thumb(path: str):
    return FileResponse(_resolve_safe(THUMB_DIR, path))


@router.get("/image/{path:path}")
async def image(path: str):
    return FileResponse(_resolve_safe(IMAGE_DIR, path))
