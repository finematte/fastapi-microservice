from fastapi import HTTPException, Depends, APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load
from datetime import datetime

from models.task import Task
from models.device import Device
from models.data import Data
from models.historical_data import HistoricalData
from models.daily_average import DailyAverage

from schemas.data import DataUpdate
from schemas.task import TaskAdd
from schemas.task import TaskUpdate

from dependencies import get_db
from core.security import get_device_id

router = APIRouter()


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
        raise HTTPException(status_code=400, detail="No devices in the database")

    return devices


@router.get("/devices/data")
async def read_device_data(
    device_id: str = Depends(get_device_id),
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
        raise HTTPException(status_code=404, detail=f"No data found for device.")

    return device_data


@router.get("/devices/tasks")
async def read_device_tasks(
    device_id: str = Depends(get_device_id), db: AsyncSession = Depends(get_db)
):
    """
    Returns tasks for given device's id
    """
    result = await db.execute(
        select(Task)
        .filter(Task.device_id == device_id, Task.status == 0)
        .options(
            Load(Task).load_only(
                Task.task_id, Task.task_number, Task.status, Task.device_id
            )
        )
    )
    tasks = result.scalars().all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for device.")

    return tasks


@router.get("/devices/data/history")
async def read_device_data_history(
    device_id: str = Depends(get_device_id), db: AsyncSession = Depends(get_db)
):
    """
    Returns daily average data from last 7 days
    """
    result = await db.execute(
        select(DailyAverage)
        .filter_by(device_id=device_id)
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
        raise HTTPException(status_code=404, detail=f"No data found for device.")

    return device_historical_data


# ----------------- POST REQUESTS -----------------
@router.post("/devices/data")
async def update_device_data(
    payload: DataUpdate,
    device_id: str = Depends(get_device_id),
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
            raise HTTPException(status_code=400, detail="Device not found.")
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

    return Response(content="Data has been updated.", status_code=200)


@router.post("/devices/tasks/add")
async def manage_device_tasks(
    task_info: TaskAdd,
    device_id: str = Depends(get_device_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Adds new task for given device_id
    """
    new_task = Task(
        device_id=device_id,
        task_number=task_info.task_number,
        status=task_info.status,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return JSONResponse(
        content={"message": "Task added successfully", "task_id": new_task.task_id}
    )


@router.put("/devices/tasks/update")
async def manage_device_tasks(
    task_info: TaskUpdate,
    device_id: int = Depends(get_device_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates the status of a task with the given task_id
    """
    result = await db.execute(
        select(Task)
        .filter(Task.device_id == device_id, Task.task_id == task_info.task_id)
        .options(
            Load(Task).load_only(
                Task.task_id, Task.task_number, Task.status, Task.device_id
            )
        )
    )

    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    elif task.status == 1:
        raise HTTPException(status_code=500, detail="Task already finished.")
    else:
        task.status = task_info.status
        await db.commit()

        return JSONResponse(
            content={
                "message": "Task status updated successfully",
                "task_id": task_info.task_id,
                "new_status": task_info.status,
            }
        )
