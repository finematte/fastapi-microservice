from datetime import datetime, timedelta
from jose import jwt, ExpiredSignatureError, JWTError
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends, status

from core.settings import Settings

JWT_SECRET_KEY = Settings.JWT_SECRET_KEY
ALGORITHM = Settings.ALGORITHM

security = HTTPBearer()


# Create JWT token for device_id
def create_device_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60 * 24)
    to_encode.update({"exp": expire})

    to_encode["sub"] = str(to_encode["sub"])

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Decode JWT token with device_id
async def get_device_id(token: HTTPAuthorizationCredentials = Depends(security)):
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
        raise credentials_exception

    device_id = payload.get("sub")
    if device_id is None:
        raise credentials_exception

    return device_id
