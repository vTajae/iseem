from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from app.api.models.QuickBooks import QuickBooksToken
# importer.import_('app.api.models.QuickBooks', globals(), locals(), ['QuickBooksToken', 'Transaction'])

# importer.import(acct="chase","key", "table")
# Plaid API to get Chase data.
# table = importer.import(acct="Quickbooks","ICM", "CASH")

# client_manager = iseem.client_manager(port=8000,nemo_security=security)\

class QuickBooksRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def save_tokens(self, access_token: str, refresh_token: str, user_id: str, realm_id: str, expires_at: int):
        # Check if a token record already exists
        
        # print(user_id, "user_id")
        
        existing_token = await self.get_latest_tokens(user_id)
        
        print(existing_token, "existing_token")
        
        if existing_token:
            # Update the existing record
            existing_token.user_id = user_id
            existing_token.access_token = access_token
            existing_token.refresh_token = refresh_token
            existing_token.realm_id = realm_id
            existing_token.expires_at = expires_at
            await self.db.commit()
        else:
            # Create a new record
            token_record = QuickBooksToken(user_id=user_id, access_token=access_token, refresh_token=refresh_token)
            print(token_record,"token_record")
            self.db.add(token_record)
            await self.db.commit()
            
    async def get_realm_id_by_user_id(self, user_id: str):
        stmt = select(QuickBooksToken.realm_id).where(QuickBooksToken.user_id == user_id).order_by(QuickBooksToken.id.desc())
        result = await self.db.execute(stmt)
        # Fetch the first record's realm_id, if it exists
        realm_id = result.scalars().first()
        
        print (realm_id, "realm_id")
        
        # Check the type of the fetched result and handle accordingly
        if isinstance(realm_id, str):
            return realm_id
        elif isinstance(realm_id, QuickBooksToken):
            return realm_id.realm_id
        else:
            return None


        
    async def get_latest_tokens(self, user_id: str):
        stmt = select(QuickBooksToken).where(QuickBooksToken.user_id == user_id).order_by(QuickBooksToken.id.desc())
        result = await self.db.execute(stmt)
        return result.scalars().first()

