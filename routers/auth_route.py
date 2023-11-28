from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import timedelta
import requests
import uuid

from schemas.device import DeviceID, AuthorizationCode
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


@router.post("/authorize_device")
async def authorize_device(
    payload: AuthorizationCode, db: AsyncSession = Depends(get_db)
):
    code = payload.code

    ruby_backend_url = "https://ruby-backend-api.greenmind.site/"

    headers = {"Content-Type": "application/json"}
    response_1 = requests.get(
        ruby_backend_url + "api/v1/auth_code",
        json={"code": code},
        headers=headers,
    )

    print(response_1.text)
    if response_1.status_code != 200:
        raise HTTPException(
            status_code=response_1.status_code, detail="Error! Invalid code."
        )
    else:
        while True:
            device_id = uuid.uuid4
            existing_device = await db.execute(
                select(Device).filter(Device.device_id == device_id)
            )
            if existing_device.scalars().first() is None:
                new_device = Device(device_id=device_id)
                db.add(new_device)
                await db.commit()
                break

        print(device_id)
        headers = {"Content-Type": "application/json"}
        response_2 = requests.post(
            ruby_backend_url + "api/v1/devices",
            json={"code": code, "device": device_id},
            headers=headers,
        )
        print(response_2.text)
        if response_2.status_code != 200:
            raise HTTPException(
                status_code=response_2.status_code,
                detail="Error! Something went wrong.",
            )
        else:
            return JSONResponse(
                content={"message": "Device authorized!", "device_id": device_id}
            )
