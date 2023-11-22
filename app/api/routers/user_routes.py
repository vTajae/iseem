# app/routers/user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import models
from app.api.schemas import user_schema,quickbooks_schema
from app.api.dependencies.database import get_db


router = APIRouter()

@router.post("/users/", response_model=user_schema.UserResponse)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    # Logic to add user to the database using SQLAlchemy models
    ...

