import datetime
from app.api.enums.token import TokenType
from app.api.models.Auth import Token
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_token(self, token: str, user_id: int, expiry_date: datetime, token_type: TokenType):
        new_token = Token(token=token, user_id=user_id, expiry_date=expiry_date, token_type=token_type)
        self.db.add(new_token)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise

    async def invalidate_token(self, token: str):
        await self.db.execute(
            update(Token)
            .where(Token.token == token)
            .values(is_active=False)
        )
        await self.db.commit()

    async def find_token(self, token: str):
        result = await self.db.execute(
            select(Token)
            .where(Token.token == token, Token.is_active == True)
        )
        return result.scalars().first()
    
    async def find_active_token_by_user(self, user_id: int, token_type: TokenType):
        result = await self.db.execute(
            select(Token)
            .where(Token.user_id == user_id, Token.token_type == token_type, Token.is_active == True)
        )
        return result.scalars().first()
