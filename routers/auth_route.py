from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import timedelta

from schemas.device import GetValidateInfo
from schemas.user import UserWithDevice
from models.user import User
from models.device import Device
from core.settings import Settings
from core.security import create_device_token

from dependencies import get_db

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = Settings.ACCESS_TOKEN_EXPIRE_MINUTES


@router.post("/request_device_token")
async def request_device_token(
    payload: GetValidateInfo, db: AsyncSession = Depends(get_db)
):
    # Verify if the device is registered
    device = await db.execute(
        select(Device).filter(Device.device_id == payload.device_id)
    )
    device = device.scalars().first()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_device_token(
        data={"sub": payload.device_id}, expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer"}


@router.post("/request_user_token")
async def request_user_token(
    payload: UserWithDevice, db: AsyncSession = Depends(get_db)
):
    # Verify if the device is registered
    user_device = await db.execute(
        select(User).filter(
            User.user_login == payload.user_login, Device.device_id == payload.device_id
        )
    )
    user_device = user_device.scalars().first()

    print(user_device)

    if not user_device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_device_token(
        data={"sub": payload.device_id}, expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer"}
