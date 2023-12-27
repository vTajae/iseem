from datetime import timedelta
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, MetaData
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.api.dependencies.database import Base  # Update with your database setup


metadata = MetaData()

class User(Base):
    
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow() + timedelta(hours=3))  
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow()) 

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}...>"
    
 