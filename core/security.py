from datetime import datetime, timedelta
from jose import jwt, ExpiredSignatureError
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends, status, Request

from core.settings import Settings

from redis_conf.redis_conn import redis_client
from redis_conf.rate_limiting_util import RateLimiter

JWT_SECRET_KEY = Settings.JWT_SECRET_KEY
ALGORITHM = Settings.ALGORITHM

security = HTTPBearer()

rate_limiter = RateLimiter(
    redis_client, threshold=5, reset_interval=timedelta(minutes=15)
)


# Create JWT token for device_id
def create_device_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    to_encode["sub"] = str(to_encode["sub"])

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Decode JWT token with device_id
async def get_device_id(
    request: Request, token: HTTPAuthorizationCredentials = Depends(security)
):
    ip = request.client.host

    if rate_limiter.is_rate_limited(ip):
        raise HTTPException(status_code=429, detail="Too many failed attempts")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token.credentials, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        rate_limiter.record_failure(ip)
        raise credentials_exception

    device_id = payload.get("sub")
    device_id = str(device_id)

    if device_id is None:
        raise credentials_exception

    rate_limiter.reset_failures(ip)
    return device_id
