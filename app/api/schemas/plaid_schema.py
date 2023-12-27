from typing import List
from pydantic import BaseModel

class LinkTokenRequest(BaseModel):
    client_user_id: str
    access_token: str
    
class LinkTokenResponse(BaseModel):
    link_token: str
    
class AccessTokenRequest(BaseModel):
    public_token: str
    
class AccessTokenResponse(BaseModel):
    access_token: str
    
class PublicTokenRequest(BaseModel):
    link_token: str
    
# Get Transactions
class TransactionResponse(BaseModel):
    latest_transactions: List[dict]

# class SandboxPublicTokenCreateRequestModel(BaseModel):
#     institution_id: str
#     initial_products: List[str]
#     link_token: str
    
class SandboxPublicTokenCreateRequestModel(BaseModel):
    link_token: str
    
class PublicTokenCreateRequestModel(SandboxPublicTokenCreateRequestModel):
    link_token: str
    user_id: str
    
class AccountModel(BaseModel):
    access_token: str
    