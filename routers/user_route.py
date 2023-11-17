from fastapi import HTTPException, Depends, APIRouter, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Load
from fastapi import HTTPException

from models.user import User

from schemas.user import NewUser


router = APIRouter()

from dependencies import get_db


@router.get("/users")
async def read_users(db: AsyncSession = Depends(get_db)):
    """
    Returns all users from the database
    """
    result = await db.execute(
        select(User).options(Load(User).load_only(User.user_login))
    )
    users = result.scalars().all()

    if not users:
        raise HTTPException(status_code=400, detail="No users in the database.")

    return users


@router.post("/create_user")
async def create_user(user_data: NewUser, db: AsyncSession = Depends(get_db)):
    """
    Adds a new user to the database
    """
    existing_user = await db.execute(
        select(User).filter(User.user_login == user_data.user_login)
    )
    if existing_user.scalars().first() is not None:
        raise HTTPException(status_code=400, detail="User already exists.")

    new_user = User(user_login=user_data.user_login)
    db.add(new_user)
    await db.commit()

    return Response(content="User created successfully.", status_code=200)
