from fastapi import Depends, APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load
from sqlalchemy import desc
from datetime import datetime

from models.data import Data
from models.historical_data import HistoricalData
from models.daily_average import DailyAverage

from slowapi import Limiter
from slowapi.util import get_remote_address

from schemas.data import DataUpdate

from main import get_client_ip
from dependencies import get_db
from core.security import get_device_id

limiter = Limiter(key_func=get_client_ip)

router = APIRouter()


# ----------------- GET REQUESTS ----------------- #
@router.get("/data")
async def read_data(request: Request, db: AsyncSession = Depends(get_db)):
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
        return JSONResponse(content={}, status_code=404)

    return data


@router.get("/devices/data")
async def read_device_data(
    device_id: int = Depends(get_device_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns data for given device's id
    """
    result = await db.execute(
        select(Data)
        .filter_by(device_id=device_id)
        .options(
            Load(Data).load_only(
                Data.device_id, Data.temp, Data.soil_hum, Data.air_hum, Data.light
            )
        )
    )
    device_data = result.scalars().all()

    if not device_data:
        return JSONResponse(content={}, status_code=404)

    return device_data


@router.get("/devices/data/history")
async def read_device_data_history(
    device_id: int = Depends(get_device_id), db: AsyncSession = Depends(get_db)
):
    """
    Returns daily average data from last 7 days
    """
    result = await db.execute(
        select(DailyAverage)
        .filter_by(device_id=device_id)
        .order_by(desc(DailyAverage.date))
        .options(
            Load(DailyAverage).load_only(
                DailyAverage.device_id,
                DailyAverage.avg_temp,
                DailyAverage.avg_soil_hum,
                DailyAverage.avg_air_hum,
                DailyAverage.avg_light,
                DailyAverage.date,
            )
        )
    )

    device_historical_data = result.scalars().all()

    if not device_historical_data:
        return JSONResponse(content={}, status_code=404)

    return device_historical_data


# ----------------- POST REQUESTS ----------------- #
@router.post("/devices/data")
async def update_device_data(
    payload: DataUpdate,
    device_id: int = Depends(get_device_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates data for a given device's id. If no data exists, creates a new data entry.
    """
    data_entry = await db.execute(select(Data).filter(Data.device_id == device_id))

    data_entry = data_entry.scalars().first()

    if not data_entry:
        try:
            new_data_entry = Data(
                device_id=device_id,
                temp=payload.temp,
                soil_hum=payload.soil_hum,
                air_hum=payload.air_hum,
                light=payload.light,
            )
            db.add(new_data_entry)
            await db.commit()
        except:
            return JSONResponse(content={}, status_code=404)
    else:
        data_entry.soil_hum = payload.soil_hum
        data_entry.light = payload.light
        data_entry.temp = payload.temp
        data_entry.air_hum = payload.air_hum
        await db.commit()

    last_entry = await db.execute(
        select(HistoricalData)
        .filter(HistoricalData.device_id == device_id)
        .order_by(HistoricalData.created_at.desc())
        .limit(1)
    )

    last_entry = last_entry.scalars().first()

    if (
        not last_entry
        or (datetime.utcnow() - last_entry.created_at).total_seconds() > 3600
    ):
        new_historical_data = HistoricalData(
            device_id=device_id,
            created_at=datetime.utcnow(),
            temp=payload.temp,
            soil_hum=payload.soil_hum,
            air_hum=payload.air_hum,
            light=payload.light,
        )
        db.add(new_historical_data)
        await db.commit()

    return JSONResponse(
        content={"message": "Data has been updated."},
        status_code=200,
    )
