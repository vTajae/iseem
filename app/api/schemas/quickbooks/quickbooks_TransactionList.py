from datetime import date, datetime
from typing import Dict, Generic, Optional, List, TypeVar
from pydantic import BaseModel
from fastapi import Query

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
    value: str
    id: Optional[str] = None

class TransactionRow(BaseModel):
    type: str
    ColData: List[TransactionData]

class TransactionsRows(BaseModel):
    Row: List[TransactionRow]

class TransactionHeader(BaseModel):
    Time: datetime
    ReportName: str
    DateMacro: Optional[str]
    StartPeriod: date
    EndPeriod: date
    Currency: str
    Option: Optional[List[Dict[str, str]]]

class Column(BaseModel):
    ColTitle: str
    ColType: str

class TransactionColumns(BaseModel):
    Column: List[Column]


class TransactionModel(BaseModel):
    Header: TransactionHeader
    Columns: TransactionColumns
    Rows: TransactionsRows


class QuickBooksQueryParams(BaseModel):
    page: int = Query(1, description="Page number", ge=1)
    limit: int = Query(10, description="Items per page", ge=1, le=100)
    minorversion: int = 70  # Static value for minorversion

T = TypeVar('T')

class Pagination(BaseModel, Generic[T]):
    data: List[T]
    page: int
    total_pages: int
    total_items: int

class PaginatedTransactionResponse(Pagination[TransactionModel]):
    pass

