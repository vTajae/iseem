# app/models/user_model.py
from sqlalchemy import Column, Integer, String
from app.api.dependencies.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
