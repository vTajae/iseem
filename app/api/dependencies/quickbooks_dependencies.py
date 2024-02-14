from fastapi import Depends
from app.api.dependencies.database import AsyncSession, async_database_session
from app.api.repository.quickbooks_repository import QuickBooksRepository
from app.api.services.quickbooks_service import QuickBooksService


# Dependency for QuickBooksService with a repository
async def get_quickbooks_service(db: AsyncSession = Depends(async_database_session.get_session)) -> QuickBooksService:
    quickbooks_repo = QuickBooksRepository(db)
    return QuickBooksService(quickbooks_repo)
