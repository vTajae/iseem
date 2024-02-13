# app/schemas/user_schema.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
        
class UserModel(BaseModel):
    id: str
    username: str
    # hashed_password: str
    # expires_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

    
class UserToken(BaseModel):
    access_token: str
    refresh_token: str

class UserResponse(BaseModel):
    user: UserModel
    tokens: UserToken
    
    class Config:
        from_attributes = True

    

class UserInDB(UserCreate):
    hashed_password: str
    
class UserRegisterSchema(BaseModel):
    username: str
    password: str

class UserLoginSchema(BaseModel):
    username: str
    password: str
    
    
    
    