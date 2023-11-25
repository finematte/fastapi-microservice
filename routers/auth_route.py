from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import timedelta

from schemas.device import DeviceID
from models.device import Device
from core.settings import Settings
from core.security import create_device_token

from dependencies import get_db

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = Settings.ACCESS_TOKEN_EXPIRE_MINUTES


@router.post("/request_token")
async def request_token(payload: DeviceID, db: AsyncSession = Depends(get_db)):
    device = await db.execute(
        select(Device).filter(Device.device_id == payload.device_id)
    )
    device = device.scalars().first()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_device_token(
        data={"sub": payload.device_id}, expires_delta=access_token_expires
    )

    return {"access_token": token}
