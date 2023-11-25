import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL_ASYNC")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_default_secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 0.5


settings = Settings()
