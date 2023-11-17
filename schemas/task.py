from pydantic import BaseModel, validator
from typing import Optional


class TaskManage(BaseModel):
    device_id: int
    task_id: Optional[int] = None
    task_number: int
    status: int

    @validator("status")
    def validate_status(cls, status):
        if status not in [0, 1, 2]:
            raise ValueError("Invalid status value. Allowed values: 0, 1, 2.")
        return status

    @validator("task_number")
    def validate_task_number(cls, task_number):
        if task_number not in [0, 1]:
            raise ValueError("Invalid task_number value. Allowed values: 0, 1.")
        return task_number
