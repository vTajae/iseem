from app.api.dependencies.user_dependencies import get_user_service
from app.api.services.user_service import UserService
from fastapi import Depends
from app.api.repository.plaid_repository import PlaidRepository
from app.api.services.plaid_service import PlaidService
from app.api.dependencies.database import AsyncSession, async_database_session


async def get_plaid_service(
    db: AsyncSession = Depends(async_database_session.get_session),
    userService: UserService = Depends(get_user_service)
) -> PlaidService:
    plaid_repo = PlaidRepository(db)
    return PlaidService(plaid_repo, userService)


