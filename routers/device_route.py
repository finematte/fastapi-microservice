from fastapi import Depends, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load
from sqlalchemy import delete
import asyncio

from models.task import Task
from models.device import Device
from models.data import Data
from models.historical_data import HistoricalData
from models.daily_average import DailyAverage

from dependencies import get_db
from core.security import get_device_id

router = APIRouter()


async def delete_device_information(device_id: int, db: AsyncSession):
    while True:
        result = await db.execute(
            select(Task).filter(
                Task.device_id == device_id,
                Task.status == 0,
                Task.task_number == 1,
            )
        )
        task = result.scalars().all()

        if not task:
            await db.execute(delete(Data).where(Data.device_id == device_id))
            await db.execute(
                delete(HistoricalData).where(HistoricalData.device_id == device_id)
            )
            await db.execute(
                delete(DailyAverage).where(DailyAverage.device_id == device_id)
            )
            await db.execute(delete(Task).where(Task.device_id == device_id))
            await db.execute(delete(Device).where(Device.device_id == device_id))

            await db.commit()
            break
        else:
            await asyncio.sleep(5)


@router.get("/devices")
async def read_devices(db: AsyncSession = Depends(get_db)):
    """
    Returns all devices from the database
    """
    result = await db.execute(
        select(Device).options(Load(Device).load_only(Device.device_id))
    )
    devices = result.scalars().all()

    if not devices:
        return JSONResponse(content={}, status_code=404)

    return devices


@router.delete("/delete_device")
async def delete_device(
    background_tasks: BackgroundTasks,
    device_id: int = Depends(get_device_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Deletes device with given device_id. Must include JWT token.
    """
    result = await db.execute(
        select(Device)
        .filter_by(device_id=device_id)
        .options(Load(Device).load_only(Device.device_id))
    )

    device = result.scalars().all()

    if not device:
        return JSONResponse(content={"message": "Device not found."}, status_code=404)
    else:
        await db.execute(delete(Task).where(Task.device_id == device_id))

        deleting_task = Task(device_id=device_id, task_number=1, status=0)

        db.add(deleting_task)
        await db.commit()

        background_tasks.add_task(delete_device_information, device_id, db)

        return JSONResponse(
            content={"message": "Device deleted successfully."}, status_code=200
        )
