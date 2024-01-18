from app.api.enums.token import TokenType
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True)
    user_id = Column(Integer)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    token_type = Column(Enum(TokenType))  # Use the Enum for token type
