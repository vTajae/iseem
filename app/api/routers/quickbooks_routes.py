from typing import Dict
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.quickbooks_dependencies import get_quickbooks_service
from app.api.models.QuickBooks import QuickBooksToken
from app.api.models.User import User
from app.api.schemas.quickbooks.quickbooks_TransactionList import PaginatedTransactionResponse, QuickBooksQueryParams, TransactionModel
from app.api.services.quickbooks_service import QuickBooksService
from fastapi import APIRouter, Depends, HTTPException, Request
from app.config.quickbooks_config import get_env_variable
from intuitlib.exceptions import AuthClientError
from fastapi.responses import HTMLResponse, RedirectResponse
from app.utils.utils import paginate_data
from intuitlib.enums import Scopes
import logging

router = APIRouter()


logger = logging.getLogger(__name__)


@router.get("/api/quickbooks/login")
async def quickbooks_login(service: QuickBooksService = Depends(get_quickbooks_service)) -> Dict[str, str]:
    try:
        auth_url = service.get_auth_url([Scopes.ACCOUNTING])
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to generate authorization URL")


@router.get("/api/quickbooks/callback")
async def quickbooks_callback(request: Request, user: User = Depends(get_current_user),
                              service: QuickBooksService = Depends(get_quickbooks_service)):
    code = request.query_params.get('code')
    if not code:
        raise HTTPException(
            status_code=400, detail="Missing authorization code")

    try:
        # The service handles the exchange of the code for tokens and saves them
        return await service.exchange_code_for_tokens(code, user.id)
    #  # Close the authentication window using JavaScript
    #     response_html = """
    #     <script>
    #       // Send a message to the parent window
    #       window.opener.postMessage('login_complete', '*');
    #       // Close the authentication window
    #       window.close();
    #     </script>
    #     """

        # return RedirectResponse("/api/quickbooks/success")

    except AuthClientError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during token exchange: {str(e)}")


@router.get("/quickbooks/{report_type}")
async def get_quickbooks_report(
    request: Request,
    report_type: str,
    query_params: QuickBooksQueryParams = Depends(),
    service: QuickBooksService = Depends(get_quickbooks_service),
    user: User = Depends(get_current_user)
):
    company_id = get_env_variable("QUICKBOOKS_COMPANY_ID")
    if not company_id:
        raise HTTPException(
            status_code=500, detail="Company ID is not set in environment variables")

    # Retrieve the access token from cookies, or use None to refresh the token
    access_token = request.cookies.get("access_token")

  # Fetch full data from QuickBooks using the access token or refreshing it
    full_data = await service.make_quickbooks_report_request(company_id, report_type, query_params.dict(), access_token, user.id)
    parsed_report = service.parse_quickbooks_report(full_data)
    paginated_response = paginate_data(parsed_report, query_params.page, query_params.limit)
    print(paginated_response, "paginated_response")
    return paginated_response


@router.get("/quickbooks/token")
async def get_access_token(current_user: User = Depends(get_current_user)):
    # Retrieve the latest token for the current user
    token_record = await QuickBooksToken.filter(user_id=current_user.id).first()
    if not token_record:
        raise HTTPException(status_code=404, detail="Token not found")
    return {"access_token": token_record.access_token}
