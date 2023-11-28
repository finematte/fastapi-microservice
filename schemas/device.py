from pydantic import BaseModel


class DeviceID(BaseModel):
    device_id: int


class AuthorizationCode(BaseModel):
    code: str
