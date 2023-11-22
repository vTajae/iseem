from fastapi import Depends
from app.api.repository.quickbooks_repository import QuickBooksRepository
from app.api.services.quickbooks_service import QuickBooksService
from app.config.quickbooks_config import client


def quickbooks_dep() -> QuickBooksService:
    quickbooks_repo = QuickBooksRepository(client)
    return QuickBooksService(quickbooks_repo)
