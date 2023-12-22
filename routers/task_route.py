from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load

from models.task import Task

from schemas.task import TaskAdd
from schemas.task import TaskUpdate

from dependencies import get_db
from core.security import get_device_id

router = APIRouter()


# ----------------- GET REQUESTS ----------------- #
@router.get("/tasks")
async def read_tasks(db: AsyncSession = Depends(get_db)):
    """
    Returns all tasks from the database
    """
    result = await db.execute(
        select(Task).options(
            Load(Task).load_only(
                Task.task_id, Task.device_id, Task.task_number, Task.status
            )
        )
    )

    tasks = result.scalars().all()

    if not tasks:
        return JSONResponse(
            json={},
            status_code=404,
        )
    else:
        return tasks


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
        return JSONResponse(content={}, status_code=404)

    return tasks


# ----------------- POST REQUESTS ----------------- #
@router.post("/devices/tasks/add")
async def manage_device_tasks(
    task_info: TaskAdd,
    device_id: int = Depends(get_device_id),
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
        content={"message": "Task added successfully", "task_id": new_task.task_id},
        status_code=200,
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
        return JSONResponse(content={"message": "Task not found."}, status_code=404)
    elif task.status == 1:
        return JSONResponse(
            content={"message": "Task already finished."}, status_code=500
        )
    else:
        task.status = task_info.status
        await db.commit()

        return JSONResponse(
            content={
                "message": "Task status updated successfully",
                "task_id": task_info.task_id,
                "new_status": task_info.status,
            },
            status_code=200,
        )
