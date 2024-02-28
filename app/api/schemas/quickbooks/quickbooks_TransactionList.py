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
    report_type: str = Query(None, description="Type of QuickBooks report")

    # Adjusted get_custom_params to return params without pre-encoding the comma
    def get_custom_params(self) -> dict:
        params = {
            "minorversion": self.minorversion,
            # Additional default params as needed
        }

        # Manually adding start_date and end_date
        start_date = "2022-02-22"  # Example start date
        end_date = "2024-02-22"    # Example end date

        # Add start_date and end_date to the query_params if they are not None
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        #         # Include start_date and end_date if they are specified
        # if self.start_date:
        #     params["start_date"] = self.start_date.strftime('%Y-%m-%d')
        # if self.end_date:
        #     params["end_date"] = self.end_date.strftime('%Y-%m-%d')

        columns_mapping = {
            "ProfitAndLossDetail": ["create_by", "create_date", "doc_num", "last_mod_by", "last_mod_date", "memo", "name", "pmt_mthd", "split_acc", "tx_date", "txn_type", "subt_nat_amount"],
            "GeneralLedger": ["account_name", "chk_print_state", "create_by", "create_date", "cust_name", "doc_num", "emp_name", "inv_date", "is_adj", "is_ap_paid", "is_ar_paid", "is_cleared", "item_name", "last_mod_by", "last_mod_date", "memo", "name", "quantity", "rate", "split_acc", "tx_date", "txn_type", "vend_name", "subt_nat_amount"],
            "APagingDetail": ["create_by", "create_date", "doc_num", "due_date", "last_mod_by", "last_mod_date", "memo", "past_due", "term_name", "tx_date", "txn_type", "vend_bill_addr", "vend_comp_name", "vend_name", "vend_pri_cont", "vend_pri_email", "vend_pri_tel", "dept_name"],
            "CustomerBalanceDetail": ["bill_addr", "create_by", "create_date", "cust_bill_email", "cust_comp_name", "cust_msg", "cust_phone_other", "cust_tel", "cust_name", "deliv_addr", "doc_num", "due_date", "last_mod_by", "last_mod_date", "memo", "sale_sent_state", "ship_addr", "ship_date", "ship_via", "term_name", "tracking_num", "tx_date", "txn_type", "sales_cust1", "sales_cust2", "sales_cust3", "dept_name"],
            "TransactionList": ["account_name", "create_by", "create_date", "cust_msg", "due_date", "doc_num", "inv_date", "is_ap_paid", "is_cleared", "is_no_post", "last_mod_by", "memo", "name", "other_account", "pmt_mthd", "printed", "sales_cust1", "sales_cust2", "sales_cust3", "term_name", "tracking_num", "tx_date", "txn_type", "dept_name"],
            "TrialBalance": ["bill_addr", "create_by", "create_date", "cust_bill_email", "cust_comp_name", "cust_msg", "cust_phone_other", "cust_tel", "cust_name", "deliv_addr", "doc_num", "due_date", "last_mod_by", "last_mod_date", "memo", "sale_sent_state", "ship_addr", "ship_date", "ship_via", "term_name", "tracking_num", "tx_date", "txn_type", "sales_cust1", "sales_cust2", "sales_cust3", "dept_name"],
        }

        if self.report_type in columns_mapping:
            # Join the columns with a comma, httpx will encode this correctly
            params["columns"] = ",".join(columns_mapping[self.report_type])
        return params



T = TypeVar('T')

class Pagination(BaseModel, Generic[T]):
    data: List[T]
    page: int
    total_pages: int
    total_items: int

class PaginatedTransactionResponse(Pagination[TransactionModel]):
    pass

