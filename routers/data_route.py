from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load
from fastapi import HTTPException

from models.data import Data

from dependencies import get_db

from core.security import get_device_id

router = APIRouter()


@router.get("/data")
async def read_data(
    db: AsyncSession = Depends(get_db), device_id: int = Depends(get_device_id)
):
    """
    Returns data for the authenticated device
    """
    result = await db.execute(
        select(Data)
        .filter(Data.device_id == device_id)
        .options(
            Load(Data).load_only(
                Data.device_id, Data.temp, Data.soil_hum, Data.air_hum, Data.light
            )
        )
    )
    data = result.scalars().all()

    if not data:
        raise HTTPException(status_code=404, detail="No data found for this device.")

    return data
