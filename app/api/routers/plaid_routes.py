# plaid_routes.py
import json
from app.api.models.User import User
from fastapi import APIRouter, Request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.api.dependencies.auth import get_current_user, get_current_user_id
from app.api.dependencies.plaid_dependencies import get_plaid_service
from app.api.schemas.plaid_schema import AccessTokenRequest, AccountModel, PublicTokenRequest, SandboxPublicTokenCreateRequestModel
from app.api.services.plaid_service import PlaidService


router = APIRouter()


@router.post("/api/plaid/create_sandbox_public_token")
async def create_sandbox_public_token(request_data: SandboxPublicTokenCreateRequestModel, service: PlaidService = Depends(get_plaid_service), user_id: int = Depends(get_current_user_id)):
    try:
        public_token = await service.create_and_exchange_sandbox_public_token(request_data, user_id)
        return JSONResponse(public_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/plaid/create_public_token")
async def create_dev_public_token(request_data: PublicTokenRequest, service: PlaidService = Depends(get_plaid_service)):
    try:
        public_token = await service.create_and_exchange_public_token(request_data.link_token)
        return {"public_token": public_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/api/plaid/create_link_token')
async def create_link_token(service: PlaidService = Depends(get_plaid_service), user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(
            status_code=401, detail="Session invalid or expired, please login.")
    user_id = user.id  # Assuming the user object has an 'id' attribute
    return service.create_link_token(user_id)


@router.get('/api/plaid/info')
async def get_info(service: PlaidService = Depends(get_plaid_service), user_id: int = Depends(get_current_user_id)):
    return await service.get_info(user_id)


@router.get('/api/plaid/accounts')
async def get_accounts(access_token: str, service: PlaidService = Depends(get_plaid_service), user_id: int = Depends(get_current_user_id)):
    return await service.get_accounts(access_token)


# @router.get('/api/auth')
# def get_auth(service: PlaidService = Depends(get_plaid_service)):
#     return service.get_auth()
