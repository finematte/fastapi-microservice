from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load
from datetime import datetime
from fastapi import HTTPException

from models.task import Task
from models.device import Device
from models.data import Data
from models.historical_data import HistoricalData
from models.daily_average import DailyAverage
from models.user import User

from schemas.data import DataUpdate
from schemas.device import NewDevice, GetValidateInfo
from schemas.task import TaskManage

from dependencies import get_db
from core.security import get_device_id

router = APIRouter()


@router.get("/devices")
async def read_devices(db: AsyncSession = Depends(get_db)):
    """
    Returns all devices from the database
    """
    result = await db.execute(
        select(Device).options(
            Load(Device).load_only(Device.device_id, Device.user_login, Device.name)
        )
    )
    devices = result.scalars().all()

    if not devices:
        raise HTTPException(status_code=400, detail="No devices in the database.")

    return devices


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
        raise HTTPException(status_code=404, detail=f"No data found for device.")

    return device_data


@router.get("/devices/tasks")
async def read_device_tasks(
    device_id: int = Depends(get_device_id), db: AsyncSession = Depends(get_db)
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
    device_id: int = Depends(get_device_id), db: AsyncSession = Depends(get_db)
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


@router.post("/devices/tasks")
async def manage_device_tasks(
    task_info: TaskManage, db: AsyncSession = Depends(get_db)
):
    """
    Updates existing task or adds a new one.
    """
    task_query = select(Task).filter(
        Task.device_id == task_info.device_id, Task.task_id == task_info.task_id
    )
    task_result = await db.execute(task_query)
    task = task_result.scalars().first()

    if task:
        task.status = task_info.status
        await db.commit()
        return Response(content="Task updated successfully.", status_code=200)
    else:
        new_task = Task(
            device_id=task_info.device_id,
            task_number=task_info.task_number,
            status=task_info.status,
        )
        db.add(new_task)
        await db.commit()

        return Response(content="Task created successfully.", status_code=200)


@router.post("/add_device")
async def add_device_to_user(
    device_data: NewDevice, db: AsyncSession = Depends(get_db)
):
    """
    Adds a new device to an existing user
    """
    user = await db.execute(
        select(User).filter(User.user_login == device_data.user_login)
    )
    user = user.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    device = await db.execute(
        select(Device).filter(Device.device_id == device_data.device_id)
    )

    if device:
        raise HTTPException(
            status_code=404, detail="Device with this ID is already in the database."
        )

    new_device = Device(
        name=device_data.name,
        user_login=device_data.user_login,
        device_id=device_data.device_id,
    )
    db.add(new_device)
    await db.commit()

    return Response(content="Device added to user successfully.", status_code=200)
