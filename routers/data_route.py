from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load

from models.data import Data

from dependencies import get_db

router = APIRouter()


@router.get("/data")
async def read_data(db: AsyncSession = Depends(get_db)):
    """
    Returns data for all devices
    """
    result = await db.execute(
        select(Data).options(
            Load(Data).load_only(
                Data.device_id, Data.temp, Data.soil_hum, Data.air_hum, Data.light
            )
        )
    )
    data = result.scalars().all()

    if not data:
        return JSONResponse(content={[]}, status_code=404)

    return data
