from datetime import date, datetime
from typing import Generic, Optional, List, TypeVar
from fastapi import Query
from pydantic import BaseModel




class QuickBooksTokenCreate(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None


class QuickBooksTokenResponse(QuickBooksTokenCreate):
    id: int
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int


class TransactionData(BaseModel):
    id: Optional[str]
    value: str

class TransactionQueryParams(BaseModel):
    start_date: date
    end_date: date
    group_by: str

class ColData(BaseModel):
    col_data: List[TransactionData]


class TransactionRow(BaseModel):
    type: str
    col_data: List[TransactionData]


class TransactionsRows(BaseModel):
    row: List[TransactionRow]


class TransactionHeader(BaseModel):
    report_name: str
    start_period: datetime
    end_period: datetime
    time: datetime
    currency: str
    # Add other fields from Header as needed


class TransactionModel(BaseModel):
    header: TransactionHeader
    rows: TransactionsRows

class QuickBooksQueryParams(BaseModel):
    page: int = Query(1, description="Page number", ge=1)
    limit: int = Query(10, description="Items per page", ge=1, le=100)
    minorversion: int = 69  # Static value for minorversion

# link-sandbox-f8e6ffb8-0e52-41e5-a870-ea3a60708911

T = TypeVar('T')

class Pagination(BaseModel, Generic[T]):
    data: List[T]
    page: int
    total_pages: int
    total_items: int

class PaginatedTransactionResponse(Pagination[TransactionData]):
    pass