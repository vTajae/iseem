from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from app.api.services.quickbooks_service import QuickBooksService
from app.api.repository.quickbooks_repository import QuickBooksRepository
from app.api.schemas.quickbooks_schema import TokenResponse, TransactionsResponse
from intuitlib.enums import Scopes

router = APIRouter()

@router.get("/quickbooks/login", response_model=None)
async def quickbooks_login(service: QuickBooksService = Depends()):
    auth_url = service.get_auth_url([Scopes.ACCOUNTING])
    return RedirectResponse(auth_url)

@router.get("/quickbooks/callback", response_model=TokenResponse)
async def quickbooks_callback(request: Request, 
                              service: QuickBooksService = Depends()):
    code = request.query_params.get('code')
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    tokens = service.exchange_code_for_tokens(code)
    # Note: If you need to save tokens using the repository, you can do it here.
    # But you should not return the repository instance or its method's result as a response.

    # Return a response that matches the TokenResponse model
    return TokenResponse(**tokens)

@router.get("/quickbooks/transactions", response_model=TransactionsResponse)
async def get_transactions(start_date: str, end_date: str, group_by: str, 
                           service: QuickBooksService = Depends()):
    transactions = await service.make_transaction_list_request("company_id", start_date, end_date, group_by)
    # Format the transactions to match the TransactionsResponse model
    return TransactionsResponse(transactions=transactions)

@router.get("/success", response_model=None)
async def success():
    return JSONResponse(content={"message": "You have successfully logged in to QuickBooks"})
