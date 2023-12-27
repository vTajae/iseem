from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.api.models.User import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_user(self, user: User):
        try:
            user_record = User(username=user.username, hashed_password=user.hashed_password)
            self.db.add(user_record)
            await self.db.commit()
            return True
        except IntegrityError:
            await self.db.rollback()
            return False

    async def get_user_by_username(self, username: str):
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_user_by_id(self, id: int):
        stmt = select(User).where(User.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    

    async def user_exists(self, username: str):
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalars().first() is not None
