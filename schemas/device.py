from pydantic import BaseModel


class DeviceID(BaseModel):
    device_id: str


class AuthorizationCode(BaseModel):
    code: str
