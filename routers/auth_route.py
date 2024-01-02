from fastapi import HTTPException, Depends, APIRouter, Request
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

from redis_conf.redis_conn import redis_client
from redis_conf.rate_limiting_util import RateLimiter

rate_limiter = RateLimiter(
    redis_client, threshold=3, reset_interval=timedelta(minutes=15)
)

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = Settings.ACCESS_TOKEN_EXPIRE_MINUTES


@router.post("/request_token")
async def request_token(
    request: Request, payload: DeviceID, db: AsyncSession = Depends(get_db)
):
    """
    Generates JWT auth token for device with given device_id.
    """
    ip = request.client.host

    if rate_limiter.is_rate_limited(ip):
        raise HTTPException(status_code=429, detail="Too many failed attempts")

    device = await db.execute(
        select(Device).filter(Device.device_id == payload.device_id)
    )
    device = device.scalars().first()

    if not device:
        rate_limiter.record_failure(ip)
        return JSONResponse(
            content={"message": "Device not found."},
            status_code=404,
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_device_token(
        data={"sub": payload.device_id}, expires_delta=access_token_expires
    )

    rate_limiter.reset_failures(ip)

    return JSONResponse(content={"access_token": token}, status_code=200)


@router.post("/authorize_device")
async def authorize_device(
    payload: AuthorizationCode, db: AsyncSession = Depends(get_db)
):
    """
    Validates pairing request from the device with Ruby backend; creates device in the database.
    """
    code = payload.code

    ruby_backend_url = "https://ruby-backend-api.greenmind.site/"

    headers = {"Content-Type": "application/json"}
    response_1 = requests.get(
        ruby_backend_url + "api/v1/auth_code",
        json={"code": code},
        headers=headers,
    )

    if response_1.status_code != 200:
        raise HTTPException(
            status_code=response_1.status_code, detail="Error! Invalid code."
        )
    else:
        while True:
            new_device_id = str(uuid.uuid4())

            existing_device = await db.execute(
                select(Device).filter(Device.device_id == new_device_id)
            )

            existing_device = existing_device.scalars().first()

            if existing_device is None:
                new_device = Device(device_id=new_device_id)
                db.add(new_device)
                await db.commit()
                break

        headers = {"Content-Type": "application/json"}
        response_2 = requests.post(
            ruby_backend_url + "api/v1/devices",
            json={"code": code, "uuid": new_device_id},
            headers=headers,
        )
        print("there")
        print(response_2.text)
        if response_2.status_code != 201:
            raise HTTPException(
                status_code=response_2.status_code,
                detail="Error! Something went wrong.",
            )
        else:
            return JSONResponse(
                content={"message": "Device authorized!", "device_id": new_device_id},
                status_code=200,
            )
