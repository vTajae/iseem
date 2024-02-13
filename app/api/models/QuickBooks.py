from datetime import timedelta
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, MetaData
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.api.dependencies.database import Base  # Update with your database setup
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


metadata = MetaData()

class QuickBooksToken(Base):
    __tablename__ = "quickbooks_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=True)
    realm_id: Mapped[str] = mapped_column(String, nullable=True)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow() + timedelta(minutes=60))  # Default to 30 days from now
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.utcnow())  # Default to 30 days from now


    user = relationship("User")
    def __repr__(self):
        return f"<QuickBooksToken(id={self.id}, access_token={self.access_token[:10]} user_id={self.user_id}...>"

# class Transaction(Base):
#     __tablename__ = 'quickbooks_transactions'

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     report_name: Mapped[str] = mapped_column(String, index=True)
#     user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
#     currency: Mapped[str] = mapped_column(String, index=True)
#     start_period: Mapped[DateTime] = mapped_column(DateTime)
#     end_period: Mapped[DateTime] = mapped_column(DateTime)
#     time: Mapped[DateTime] = mapped_column(DateTime)
    
#     user = relationship("User")

