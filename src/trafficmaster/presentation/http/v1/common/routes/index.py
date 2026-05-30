from typing import Final

from fastapi import APIRouter

router: Final[APIRouter] = APIRouter(tags=["main"])


@router.get("/")
async def index() -> dict[str, str]:
    return {"message": "Hello there! Welcome to FastAPI!"}
