from typing import Dict
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.quickbooks_dependencies import get_quickbooks_service
from app.api.models.QuickBooks import QuickBooksToken
from app.api.models.User import User
from app.api.schemas.quickbooks.quickbooks_TransactionList import QuickBooksQueryParams
from app.api.services.quickbooks_service import QuickBooksService
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from intuitlib.exceptions import AuthClientError
from app.utils.utils import paginate_data
from intuitlib.enums import Scopes
import logging

router = APIRouter()


logger = logging.getLogger(__name__)


@router.get("/api/quickbooks/login")
async def quickbooks_login(service: QuickBooksService = Depends(get_quickbooks_service)) -> Dict[str, str]:
    try:
        auth_url = service.get_auth_url([Scopes.ACCOUNTING])
        print(auth_url, "auth_url")
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to generate authorization URL")


@router.get("/api/quickbooks/callback")
async def quickbooks_callback(request: Request, user: User = Depends(get_current_user),
                              service: QuickBooksService = Depends(get_quickbooks_service)):
    code = await request.query_params.get('code')
    realm_id = await request.query_params.get('realm_id')


    if not code and not realm_id:
        raise HTTPException(
            status_code=400, detail="Missing authorization code or realm_id")

    try:
        # The service handles the exchange of the code for tokens and saves them
        
        return await service.exchange_code_for_tokens(code, user.id, realm_id)

    except AuthClientError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=600, detail=f"Error during token exchange: {str(e)}")


@router.get("/quickbooks/{report_type}")
async def get_quickbooks_report(
    request: Request,
    report_type: str,
    query_params: QuickBooksQueryParams = Depends(),
    service: QuickBooksService = Depends(get_quickbooks_service),
    user: User = Depends(get_current_user),
):
    # Retrieve the access token from cookies, or use None to refresh the token
    access_token = request.cookies.get("access_token")

  # Fetch full data from QuickBooks using the access token or refreshing it
    full_data = await service.make_quickbooks_report_request(report_type, query_params.dict(), access_token, user.id)
    print(full_data, "full_data")
    parsed_report = service.parse_quickbooks_report(full_data)
    paginated_response = paginate_data(
        parsed_report, query_params.page, query_params.limit)
    return paginated_response


@router.get("/api/quickbooks/token")
async def get_access_token(current_user: User = Depends(get_current_user)):
    # Retrieve the latest token for the current user
    token_record = await QuickBooksToken.filter(user_id=current_user.id).first()
    if not token_record:
        raise HTTPException(status_code=404, detail="Token not found")
    return {"access_token": token_record.access_token}


@router.get("/api/quickbooks/refresh")
async def refresh_token(request: Request, response: Response, quickbooks_service: QuickBooksService = Depends(get_quickbooks_service), user: User = Depends(get_current_user)):
    old_refresh_token = request.cookies.get("refresh_token")
    
    # print(old_refresh_token, "old_refresh_token")

    if not old_refresh_token:
        raise HTTPException(status_code=403, detail="Refresh token not found")

    # Assuming `refresh_access_token_if_needed` handles the logic to check token expiration and refreshes if needed.
    tokens = await quickbooks_service.refresh_access_token_if_needed(user.id)
    # Set the new refresh token in a secure HttpOnly cookie
    response.set_cookie(key="refresh_token", value=tokens["refresh_token"],
                        httponly=True, secure=True, max_age=100*24*60*60)  # 100 days

    # Return the new access token in the response body
    return {"access_token": tokens["access_token"], "message": "Access token refreshed"}
