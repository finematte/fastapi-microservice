from pydantic import BaseModel, validator


class NewDevice(BaseModel):
    user_login: str
    device_id: int
    name: str


class GetValidateInfo(BaseModel):
    device_id: int
