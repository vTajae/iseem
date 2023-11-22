from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str

class UserInfoResponse(BaseModel):
    user_id: str
    user_name: str
    email: str
    
class Transaction(BaseModel):
    id: str
    amount: float
    date: str
    description: Optional[str] = None

class TransactionsResponse(BaseModel):
    transactions: List[Transaction]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str

class UserInfoResponse(BaseModel):
    user_id: str
    user_name: str
    email: str





    
# link-sandbox-f8e6ffb8-0e52-41e5-a870-ea3a60708911