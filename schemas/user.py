from pydantic import BaseModel, validator


class NewUser(BaseModel):
    user_login: str


class UserWithDevice(BaseModel):
    user_login: str
    device_id: int
