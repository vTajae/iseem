# services/quickbooks_service.py

from datetime import datetime, timezone
import json
import os
from app.api.schemas.quickbooks.quickbooks_CashFlow import CashFlowColumns, CashFlowData, CashFlowHeader, CashFlowReport, CashFlowRow, CashFlowRows, CashFlowSummary, TransactionHeader
from fastapi import HTTPException
from intuitlib.client import AuthClient
from intuitlib.exceptions import AuthClientError
from app.config.quickbooks_config import QUICKBOOKS_CLIENT_ID, QUICKBOOKS_SECRET, QUICKBOOKS_REDIRECT_URI, QUICKBOOKS_ENV
from app.api.repository.quickbooks_repository import QuickBooksRepository
import httpx
import logging


class QuickBooksService:
    def __init__(self, repo: QuickBooksRepository):
        self.auth_client = AuthClient(
            client_id=QUICKBOOKS_CLIENT_ID,
            client_secret=QUICKBOOKS_SECRET,
            redirect_uri=QUICKBOOKS_REDIRECT_URI,
            environment=QUICKBOOKS_ENV)
        self.repo = repo

    def is_token_expired(self, tokens):
        now_utc_aware = datetime.utcnow().replace(tzinfo=timezone.utc)
        return now_utc_aware >= tokens.expires_at

    def get_auth_url(self, scopes):
        if not scopes:
            raise ValueError("Scopes must not be empty")

        try:
            auth_url = self.auth_client.get_authorization_url(scopes)
            return auth_url
        except AuthClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def refresh_access_token_if_needed(self, user_id):
        tokens = await self.repo.get_latest_tokens()

        if tokens is None:
            logging.error("No tokens found in the database.")
            # Trigger re-authentication flow or inform the user
            raise HTTPException(
                status_code=401, detail="Authentication required")

        if self.is_token_expired(tokens):
            try:
                logging.info("Refreshing QuickBooks access token...")
                self.auth_client.refresh_token = tokens.refresh_token
                self.auth_client.refresh()  # Await the refresh

                new_tokens = {
                    "access_token": self.auth_client.access_token,
                    "refresh_token": self.auth_client.refresh_token
                }

                logging.info("New tokens obtained, saving to repository.")
                await self.repo.save_tokens(
                    new_tokens['access_token'], new_tokens['refresh_token'], user_id)
            except AuthClientError as e:
                logging.error(f"Error refreshing token: {e}")
                raise HTTPException(status_code=e.status_code,
                                    detail="Token refresh failed")

        return await self.repo.get_latest_tokens()

    async def exchange_code_for_tokens(self, code, user_id):
        try:
            self.auth_client.get_bearer_token(code)
            access_token = self.auth_client.access_token
            refresh_token = self.auth_client.refresh_token

            await self.repo.save_tokens(access_token, refresh_token, user_id)
            return {"access_token": access_token, "refresh_token": refresh_token}
        except AuthClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def make_quickbooks_report_request(self, company_id, report_type, query_params: dict, access_token, user_id):
        if access_token:
            tokens = await self.refresh_access_token_if_needed(user_id)
            if not tokens:
                raise HTTPException(
                    status_code=401, detail="Authentication required")
            token_to_use = tokens.access_token
        else:
            token_to_use = access_token

        # print(token_to_use, "token_to_use")

        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/reports/{report_type}"
        headers = {
            "Authorization": f"Bearer {token_to_use}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            return response.json()

    # def parse_transaction_list_report(self, report_data):

    #                   # Get the current directory of the quickbooks_service.py file
    #     current_directory = os.path.dirname(os.path.abspath(__file__))

    #     # Define the relative path to the JSON file
    #     json_file_path = os.path.join(current_directory, '..', '..', 'Transactions.json')

    # # Step 2: Open and read the JSON file
    #     with open(json_file_path, 'r') as json_file:
    #         report_data = json.load(json_file)

    #     # Extract the header and columns
    #     header = report_data.get('Header', {})
    #     columns = report_data.get('Columns', {}).get('Column', [])

    #     # Generate a list of column titles for mapping
    #     column_titles = [col.get('ColTitle', 'Unknown') for col in columns]

    #     # Extract rows and transform each row
    #     rows = report_data.get('Rows', {}).get('Row', [])

    #     # Check if rows is not empty and is a list
    #     if rows and isinstance(rows, list):
    #         transformed_rows = [self.transform_row(row, column_titles) for row in rows]
    #     else:
    #         transformed_rows = []

    #     return {"header": header, "rows": transformed_rows}

    def parse_cashflow_report(self, report_data):
        
        
        # Get the current directory of the quickbooks_service.py file
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Define the relative path to the JSON file
        json_file_path = os.path.join(
            current_directory, '..', '..', 'CashFlow.json')

    # Step 2: Open and read the JSON file
        with open(json_file_path, 'r') as json_file:
            report_data = json.load(json_file)
        # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {}).get('Column', [])
        rows = report_data.get('Rows', {})

        return {
            "header": header,
            "columns": columns,
            "rows": rows
        }

    def parse_transaction_list_report(self, report_data):

        # Get the current directory of the quickbooks_service.py file
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Define the relative path to the JSON file
        json_file_path = os.path.join(
            current_directory, '..', '..', 'Transactions.json')

    # Step 2: Open and read the JSON file
        with open(json_file_path, 'r') as json_file:
            report_data = json.load(json_file)
        # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {})

        # Extract rows and keep them in raw format
        rows = report_data.get('Rows', {})

        return {"header": header, "columns": columns, "rows": rows}

    def parse_quickbooks_report(self, report_data):
        report_name = report_data.get(
            'Header', {}).get('ReportName', '').lower()

        if report_name == 'cashflow':
            return self.parse_cashflow_report(report_data)
        elif report_name == 'transactionlist':
            return self.parse_transaction_list_report(report_data)
        else:
            return {"message": "Unknown report type or no data available."}
