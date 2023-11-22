# services/quickbooks_service.py

from fastapi import HTTPException
from intuitlib.client import AuthClient
from intuitlib.exceptions import AuthClientError
from sqlalchemy import DateTime
from app.config.quickbooks_config import QUICKBOOKS_CLIENT_ID, QUICKBOOKS_SECRET, QUICKBOOKS_REDIRECT_URI, QUICKBOOKS_ENV
from app.api.repository.quickbooks_repository import QuickBooksRepository
import httpx

class QuickBooksService:
    def __init__(self, repo: QuickBooksRepository):
        self.auth_client = AuthClient(
            QUICKBOOKS_CLIENT_ID, 
            QUICKBOOKS_SECRET, 
            QUICKBOOKS_REDIRECT_URI, 
            QUICKBOOKS_ENV        )
        self.repo = repo
    
    def is_token_expired(self, tokens):
        if tokens.expires_at:
            return DateTime.utcnow() >= tokens.expires_at
        return True 

    async def refresh_access_token_if_needed(self):
        if self.is_token_expired():
            try:
                self.auth_client.refresh()
                new_tokens = {
                    "access_token": self.auth_client.access_token,
                    "refresh_token": self.auth_client.refresh_token
                }
                self.repo.save_tokens(new_tokens)
            except AuthClientError as e:
                raise HTTPException(status_code=e.status_code, detail=str(e))
        return self.repo.get_latest_tokens()
    

    def get_auth_url(self, scopes):
        try:
            return self.auth_client.get_authorization_url(scopes)
        except AuthClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def exchange_code_for_tokens(self, code):
        try:
            self.auth_client.get_bearer_token(code)
            tokens = {
                "access_token": self.auth_client.access_token,
                "refresh_token": self.auth_client.refresh_token
            }
            self.repo.save_tokens(tokens)
            return tokens
        except AuthClientError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def make_transaction_list_request(self, company_id, start_date, end_date, group_by):
        tokens = await self.refresh_access_token_if_needed()
        if not tokens:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/reports/TransactionList"
        params = {"start_date": start_date, "end_date": end_date, "group_by": group_by}
        headers = {
            "Authorization": f"Bearer {tokens['access_token']}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

