from fastapi import APIRouter, status

router: APIRouter = APIRouter(
    prefix="/healthcheck",
    tags=["healthcheck"],
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_status() -> dict[str, str]:

    return {"message": "OK", "status": "success"}
