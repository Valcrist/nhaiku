from fastapi import APIRouter, HTTPException
from core.database import adjust_votes

router = APIRouter(
    prefix="/vote",
    tags=["vote"],
)


@router.get("/up/{manga_id:int}")
async def vote_up(manga_id: int) -> dict[str, int]:
    votes = await adjust_votes(manga_id, 1)
    if votes is None:
        raise HTTPException(status_code=404, detail="Manga not found")
    return {"votes": votes}


@router.get("/down/{manga_id:int}")
async def vote_down(manga_id: int) -> dict[str, int]:
    votes = await adjust_votes(manga_id, -1)
    if votes is None:
        raise HTTPException(status_code=404, detail="Manga not found")
    return {"votes": votes}
