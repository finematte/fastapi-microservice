from fastapi import Response, APIRouter

router = APIRouter()


@router.get("/")
async def default_page():
    """
    Default message
    """

    return Response(content="200", status_code=200)
