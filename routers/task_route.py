from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load

from models.task import Task

from dependencies import get_db

router = APIRouter()


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

    return tasks
