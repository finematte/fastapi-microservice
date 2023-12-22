from pydantic import BaseModel, validator


class DataUpdate(BaseModel):
    temp: float
    soil_hum: float
    air_hum: float
    light: float

    @validator("temp")
    def validate_temp(cls, temp):
        if temp < -10.0 or temp > 100.0:
            raise ValueError(
                "Invalid temperature value. Allowed range: -10.0 to 100.0."
            )
        return temp

    @validator("soil_hum")
    def validate_soil_hum(cls, soil_hum):
        if soil_hum < 0.0 or soil_hum > 66000.0:
            raise ValueError(
                "Invalid soil humidity value. Allowed range: 0.0 to 66000.0."
            )
        return soil_hum

    @validator("air_hum")
    def validate_air_hum(cls, air_hum):
        if air_hum < 0 or air_hum > 100:
            raise ValueError("Invalid air humidity value. Allowed range: 0 to 100.")
        return air_hum

    @validator("light")
    def validate_light(cls, light):
        if light < 0.0 or light > 51000.0:
            raise ValueError("Invalid light value. Allowed range: 0.0 to 51000.0.")
        return light
