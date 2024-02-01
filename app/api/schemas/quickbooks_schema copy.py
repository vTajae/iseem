from datetime import date, datetime
from typing import Dict, Generic, Optional, List, TypeVar
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
    col_data: List[ColData]



class TransactionsRows(BaseModel):
    row: List[TransactionRow]



class TransactionHeader(BaseModel):
    Time: datetime
    ReportName: str
    DateMacro: Optional[str]
    StartPeriod: date
    EndPeriod: date
    Currency: str
    Option: Optional[List[Dict[str, str]]]


class TransactionColumn(BaseModel):
    ColTitle: str  # Updated to match the data
    ColType: str   # Updated to match the data


class TransactionColumns(BaseModel):
    columns: List[TransactionColumn]

class TransactionModel(BaseModel):
    header: TransactionHeader
    columns: TransactionColumns  # Include the columns here
    rows: TransactionsRows


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
