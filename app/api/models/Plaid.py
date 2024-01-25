from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey
from app.api.dependencies.database import Base
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.orm.properties import MappedColumn

class PlaidDetails(Base):
    __tablename__ = 'plaid_details'
    id = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = MappedColumn(Integer, ForeignKey('users.id'), nullable=False)
    access_token = Column(String, nullable=False)
    payment_id = Column(String)
    transfer_id = Column(String)
    item_id = Column(String)
    
    user = relationship("User")
    


class PlaidToken(Base):
    __tablename__ = 'plaid_tokens'

    id = Column(Integer, primary_key=True)
    user_id: Mapped[int] = MappedColumn(Integer, ForeignKey('users.id'), nullable=False)
    access_token = Column(String, nullable=False)
    item_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)  

    # Relationship to the User model
    user = relationship("User")
    # Add other fields as necessary

    
    
