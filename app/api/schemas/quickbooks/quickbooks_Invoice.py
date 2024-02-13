from typing import List, Optional
from pydantic import BaseModel

class TaxCodeRef(BaseModel):
    value: str

class ItemRef(BaseModel):
    name: Optional[str] = None
    value: str

class TaxLineDetail(BaseModel):
    TaxRateRef: TaxCodeRef
    PercentBased: bool
    TaxPercent: int
    NetAmountTaxable: float

class TaxLine(BaseModel):
    DetailType: str
    Amount: float
    TaxLineDetail: TaxLineDetail

class TxnTaxDetail(BaseModel):
    TxnTaxCodeRef: TaxCodeRef
    TotalTax: float
    TaxLine: List[TaxLine]

class SalesItemLineDetail(BaseModel):
    ItemRef: ItemRef
    UnitPrice: float
    Qty: int
    TaxCodeRef: Optional['TaxCodeRef'] = None

class Line(BaseModel):
    Id: str
    LineNum: Optional[int] = None
    Description: Optional[str] = None
    Amount: float
    DetailType: str
    SalesItemLineDetail: Optional['SalesItemLineDetail'] = None

class Address(BaseModel):
    Id: str
    Line1: str
    Line2: Optional[str] = None
    Line3: Optional[str] = None
    Line4: Optional[str] = None
    City: Optional[str] = None
    CountrySubDivisionCode: Optional[str] = None
    PostalCode: Optional[str] = None
    Lat: Optional[str] = None
    Long: Optional[str] = None

class Invoice(BaseModel):
    TxnDate: str
    domain: str
    PrintStatus: str
    SalesTermRef: TaxCodeRef
    TotalAmt: float
    Line: List[Line]
    DueDate: str
    ApplyTaxAfterDiscount: bool
    DocNumber: str
    sparse: bool
    CustomerMemo: Optional[dict] = None
    ProjectRef: Optional[TaxCodeRef] = None
    Deposit: float
    Balance: float
    CustomerRef: ItemRef
    TxnTaxDetail: TxnTaxDetail
    SyncToken: str
    LinkedTxn: List[dict]
    BillEmail: Optional[dict] = None
    ShipAddr: Optional[Address] = None
    EmailStatus: str
    BillAddr: Optional[Address] = None
    MetaData: Optional[dict] = None
    CustomField: Optional[List[dict]] = None
    Id: str

class InvoiceQueryResponse(BaseModel):
    Invoice: List[Invoice]
    startPosition: int
    maxResults: int
    totalCount: int

class QuickBooksInvoiceReport(BaseModel):
    QueryResponse: InvoiceQueryResponse
    time: str
