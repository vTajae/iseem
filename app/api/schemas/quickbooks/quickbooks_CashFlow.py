from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

class CashFlowData(BaseModel):
    value: str
    id: Optional[str] = None

class Column(BaseModel):
    ColTitle: str
    ColType: str
    MetaData: Optional[List[Dict[str, str]]] = None


class CashFlowHeader(BaseModel):
    ColData: List[CashFlowData]

class CashFlowSummary(BaseModel):
    ColData: List[CashFlowData]

class CashFlowRow(BaseModel):
    ColData: List[CashFlowData]
    type: Optional[str]
    group: Optional[str]
    Header: Optional[CashFlowHeader]
    Summary: Optional[CashFlowSummary]
    Rows: Optional[List['CashFlowRow']]  # Recursive definition

CashFlowRow.update_forward_refs()  # Resolves the recursive definition

class CashFlowRows(BaseModel):
    Row: List[CashFlowRow]

class CashFlowColumns(BaseModel):
    Column: List[Column]

class TransactionHeader(BaseModel):
    Time: datetime
    ReportName: str
    DateMacro: Optional[str]
    StartPeriod: date
    EndPeriod: date
    Currency: str
    SummarizeColumnsBy: Optional[str]
    Option: Optional[List[Dict[str, str]]]

class CashFlowReport(BaseModel):
    Header: TransactionHeader
    Columns: CashFlowColumns
    Rows: CashFlowRows
