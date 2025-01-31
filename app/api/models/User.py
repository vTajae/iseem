from datetime import timedelta
from datetime import datetime
import uuid
from app.api.enums.token import TokenType
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, MetaData
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.api.dependencies.database import Base  # Update with your database setup
from sqlalchemy.dialects.postgresql import ENUM



metadata = MetaData()

class User(Base):
    
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow() + timedelta(hours=3))  
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow()) 

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}...>"
    
    

class Token(Base):
    
    __tablename__ = 'tokens'
    
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    token_type = Column(ENUM(TokenType, create_type=True, name='tokentype', metadata=Base.metadata)) 
    
 