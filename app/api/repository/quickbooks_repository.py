# quickbooks_repository.py

from sqlalchemy import DateTime
from sqlalchemy.orm import Session
from app.api.models.QuickBooks import QuickBooksToken  # Adjust the import path as needed

class QuickBooksRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_tokens(self, access_token, refresh_token):
        token_record = QuickBooksToken(access_token=access_token, refresh_token=refresh_token)
        self.db.add(token_record)
        self.db.commit()
        
    def get_latest_tokens(self):
        return self.db.query(QuickBooksToken).order_by(QuickBooksToken.id.desc()).first()
    
    def is_token_expired(self, tokens):
            if tokens.expires_at:
                return DateTime.utcnow() >= tokens.expires_at
            return True