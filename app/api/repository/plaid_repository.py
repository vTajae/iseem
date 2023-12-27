import time
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.models.Plaid import PlaidDetails, PlaidToken
from app.config.plaid_config import PLAID_PRODUCTS
from app.utils.utils import CustomJSONEncoder
from sqlalchemy.ext.asyncio import AsyncSession


import plaid
from plaid.model.payment_amount import PaymentAmount
from plaid.model.payment_amount_currency import PaymentAmountCurrency
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.recipient_bacs_nullable import RecipientBACSNullable
from plaid.model.payment_initiation_address import PaymentInitiationAddress
from plaid.model.payment_initiation_recipient_create_request import PaymentInitiationRecipientCreateRequest
from plaid.model.payment_initiation_payment_create_request import PaymentInitiationPaymentCreateRequest
from plaid.model.payment_initiation_payment_get_request import PaymentInitiationPaymentGetRequest
from plaid.model.link_token_create_request_payment_initiation import LinkTokenCreateRequestPaymentInitiation
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.asset_report_create_request import AssetReportCreateRequest
from plaid.model.asset_report_create_request_options import AssetReportCreateRequestOptions
from plaid.model.asset_report_user import AssetReportUser
from plaid.model.asset_report_get_request import AssetReportGetRequest
from plaid.model.asset_report_pdf_get_request import AssetReportPDFGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.identity_get_request import IdentityGetRequest
from plaid.model.investments_transactions_get_request_options import InvestmentsTransactionsGetRequestOptions
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.transfer_authorization_create_request import TransferAuthorizationCreateRequest
from plaid.model.transfer_create_request import TransferCreateRequest
from plaid.model.transfer_get_request import TransferGetRequest
from plaid.model.transfer_network import TransferNetwork
from plaid.model.transfer_type import TransferType
from plaid.model.transfer_authorization_user_in_request import TransferAuthorizationUserInRequest
from plaid.model.ach_class import ACHClass
from plaid.model.transfer_create_idempotency_key import TransferCreateIdempotencyKey
from plaid.model.transfer_user_address_in_request import TransferUserAddressInRequest


class PlaidRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_token(self, user_id: int, access_token: str, item_id: int):
        token = PlaidToken(user_id=user_id,
                      access_token=access_token, item_id=item_id)
        self.db.add(token)
        await self.db.commit()  # Use await for async commit
        return token

    async def save_plaid_token(self, user_id: int, access_token: str, item_id: str):
        plaid_token = PlaidToken(
            user_id=user_id, access_token=access_token, item_id=item_id)
        self.db.add(plaid_token)
        await self.db.commit()
    
    async def get_info(self, user_id: int):
        query = (
            select(PlaidToken)
            .where(PlaidToken.user_id == user_id)
            .order_by(PlaidToken.created_at.desc())  # Replace 'created_at' with your timestamp column
            .limit(1)
        )
        result = await self.db.execute(query)
        plaid_token = result.scalar_one_or_none()
        if plaid_token:
            return {
                'item_id': plaid_token.item_id,
                'access_token': plaid_token.access_token,
                'products': PLAID_PRODUCTS
            }
        return None
