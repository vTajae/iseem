# Now you can use plaid_client to interact with Plaid API
from app.api.services.user_service import UserService
from fastapi import Depends
from app.api.dependencies.auth import get_current_user_id
from app.api.models.Plaid import PlaidToken
from app.api.schemas.plaid_schema import AccountModel, PublicTokenCreateRequestModel
from app.api.services.base_service import BaseService
from app.api.repository.plaid_repository import PlaidRepository
from app.config.plaid_config import PLAID_PRODUCTS, PLAID_REDIRECT_URI
import plaid
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
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
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
import json
from app.config.plaid_config import client
from app.utils.utils import format_error, pretty_print_response


class PlaidService(BaseService):
    def __init__(self, repo: PlaidRepository, userService: UserService):
        self.repo = repo
        self.client = client
        self.userService = userService

    def create_link_token(self, user_id: int):
        # print("user_id", user_id)
        client_user_id = str(user_id)
        # Create a link_token for the given user
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="Plaid Test App",
            country_codes=[CountryCode('US')],
            redirect_uri=PLAID_REDIRECT_URI,
            language='en',
            # webhook='https://webhook.example.com',
            user=LinkTokenCreateRequestUser(
                client_user_id=client_user_id
            )
        )
        response = self.client.link_token_create(request)
        # Send the data to the client
        return response.to_dict()  # Return a dictionary

    async def set_access_token(self, public_token):
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        response = await self.client.item_public_token_exchange(exchange_request)

        # Save response['access_token'] and response['item_id'] to the database as needed

        # Return a response
        return {'public_token_exchange': 'complete', 'response': response.to_dict()}

    async def get_info(self, user_id: int):
        return await self.repo.get_info(user_id)

    async def create_and_exchange_sandbox_public_token(self, request_data, user_id):
        request_data = "ins_109508"
        initial_products = ["auth", "transactions"]
        products_list = [Products(product)
                         for product in initial_products]

        pt_request = SandboxPublicTokenCreateRequest(
            institution_id=request_data,
            initial_products=products_list,
        )

        pt_response = self.client.sandbox_public_token_create(pt_request)
        public_token = pt_response['public_token']

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token,

        )

        # If this method is also synchronous, remove 'await'
        exchange_response = self.client.item_public_token_exchange(
            exchange_request)

        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        await self.repo.save_plaid_token(user_id, access_token, item_id)

        # Convert to dictionary
        # Assuming the response object has a .to_dict() method
        response_dict = exchange_response.to_dict()
        return response_dict

    async def create_and_exchange_public_token(self, request_data: PublicTokenCreateRequestModel):

        public_token = request_data['public_token']

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )

        # If this method is also synchronous, remove 'await'
        exchange_response = self.client.item_public_token_exchange(
            exchange_request)

        # Save the access token using the repository if necessary
        # await self.repo.save_access_token(access_token)

        return exchange_response

    async def get_accounts(self, access_token: str):
        # print("access_token", access_token)

        try:
            request = AccountsGetRequest(access_token=access_token)
            accounts_response = self.client.accounts_get(request)
        except plaid.ApiException as e:
            response = json.loads(e.body)
            return ({'error': {'status_code': e.status, 'display_message': response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}})
        # print(accounts_response, "Plaid Response")
        return (accounts_response.to_dict())
