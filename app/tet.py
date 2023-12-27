    async def make_quickbooks_report_request(self, company_id, report_type, query_params: dict):
        tokens = await self.refresh_access_token_if_needed()
        if not tokens:
            raise HTTPException(status_code=401, detail="Authentication required")

        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/reports/{report_type}"

        headers = {
            "Authorization": f"Bearer {tokens.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            return response.json()

    async def get_transactions_paginated(self, company_id, report_type, query_params: dict):
        # Add 'page' and 'limit' query parameters when calling the repository method.
        return await self.repo.get_transactions_paginated(company_id, report_type, query_params)

    @router.get("/quickbooks/{report_type}")
    async def get_quickbooks_report(
        report_type: str,
        query_params: QuickBooksQueryParams = Depends(),
        service: QuickBooksService = Depends(get_quickbooks_service)
    ):
        company_id = get_env_variable("QUICKBOOKS_COMPANY_ID")

        # Convert the Pydantic model to a dictionary, excluding 'page' and 'limit' if necessary
        query_params_dict = {k: v for k, v in query_params.dict().items() if k not in ['page', 'limit']}
        
        report = await service.make_quickbooks_report_request(company_id, report_type, query_params_dict)
        return report


    async def get_transactions_paginated(self, page: int = 1, limit: int = 10, columns=None, sort=None, filter=None):
        # Construct your query here
        query = select(Transaction).order_by(Transaction.date.desc())
        # Use the pagination utility function
        return await get_response_paginated(self.db, Transaction, page, limit, columns, sort, filter)



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


class UserInfoResponse(BaseModel):
    user_id: str
    user_name: str
    email: str

class QuickBooksQueryParams(BaseModel):
    page: int = Query(1, description="Page number", ge=1)
    limit: int = Query(10, description="Items per page", ge=1, le=100)
    minorversion: int = 69  # Static value for minorversion
