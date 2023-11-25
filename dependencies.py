from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.settings import Settings

# Load environment variables
load_dotenv()

DATABASE_URL = Settings.DATABASE_URL


# Creating database connection
engine = create_async_engine(DATABASE_URL, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Dependency for getting the database session
async def get_db():
    async with async_session() as session:
        yield session
