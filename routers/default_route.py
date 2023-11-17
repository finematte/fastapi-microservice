from fastapi import Response, APIRouter

router = APIRouter()


@router.get("/")
async def default_page():
    """
    Default message
    """

    return Response(content="Hi there :)", status_code=200)
