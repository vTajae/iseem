from fastapi import Depends
from app.api.dependencies.database import AsyncSession, async_database_session
from app.api.repository.user_repository import UserRepository
from app.api.services.user_service import UserService
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer


# Dependency for UserService with a repository
async def get_user_service(db: AsyncSession = Depends(async_database_session.get_session)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

