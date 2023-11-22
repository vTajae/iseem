# models.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.api.dependencies.database import Base  # Update with your database setup

class QuickBooksToken(Base):
    __tablename__ = "quickbooks_tokens"
    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True))  # Add this line
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<QuickBooksToken(id={self.id}, access_token={self.access_token[:10]}...>"



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




from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/token", response_model=TokenResponse)
async def token_endpoint():
    # Logic to create a token
    token_data = {
        "access_token": "some_access_token",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "some_refresh_token"
    }
    return TokenResponse(**token_data)

@app.get("/user_info", response_model=UserInfoResponse)
async def user_info_endpoint():
    # Logic to retrieve user info
    user_info = {
        "user_id": "12345",
        "user_name": "John Doe",
        "email": "johndoe@example.com"
    }
    return UserInfoResponse(**user_info)
