from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from app.api.models.QuickBooks import QuickBooksToken
# importer.import_('app.api.models.QuickBooks', globals(), locals(), ['QuickBooksToken', 'Transaction'])

# importer.import(acct="chase","key", "table")
# Plaid API to get Chase data.
# table = importer.import(acct="Quickbooks","ICM", "CASH")

# client_manager = iseem.client_manager(port=8000,nemo_security=security)


class QuickBooksRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def save_tokens(self, access_token, refresh_token, user_id):
        # Check if a token record already exists
        existing_token = await self.get_latest_tokens()
        # print(existing_token, "existing_token")
        
        if existing_token:
            # Update the existing record
            existing_token.user_id = user_id
            existing_token.access_token = access_token
            existing_token.refresh_token = refresh_token
            existing_token.expires_at = datetime.utcnow() + timedelta(minutes=60)
        else:
            # Create a new record
            token_record = QuickBooksToken(user_id=user_id,access_token=access_token, refresh_token=refresh_token)
            self.db.add(token_record)
        await self.db.commit()

    
    
    async def get_latest_tokens(self):
        stmt = select(QuickBooksToken).order_by(QuickBooksToken.id.desc())
        result = await self.db.execute(stmt)
        return result.scalars().first()