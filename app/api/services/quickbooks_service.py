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
        return now_utc_aware >= tokens

    def get_auth_url(self, scopes):
        if not scopes:
            raise ValueError("Scopes must not be empty")

        try:
            auth_url = self.auth_client.get_authorization_url(scopes)
            return auth_url
        except AuthClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def refresh_access_token_if_needed(self, user_id):

        tokens = await self.repo.get_latest_tokens(user_id)

        # Check if tokens exist and if the access token has expired

        # print(self.is_token_expired(tokens.expires_at), "self.is_token_expired(tokens.expires_at)")

        if not tokens or self.is_token_expired(tokens.expires_at):
            # Refresh the token using the stored refresh token

            print(tokens.refresh_token, "tokens")

        try:
            self.auth_client.refresh(
                refresh_token=tokens.refresh_token)
        except AuthClientError as e:
            # just printing here but it can be used for retry workflows, logging, etc
            print(e.status_code)
            print(e.content)
            print(e.intuit_tid)

            # Assume new_tokens is a dictionary with 'access_token' and 'refresh_token' keys
            # Save the new tokens
            # Ensure you pass all required parameters to save_tokens
            await self.repo.save_tokens(tokens.access_token, tokens.refresh_token, user_id, tokens.realm_id)
            # Return the new tokens as a dictionary for consistency
            return {
                'access_token': tokens.access_token,
                'refresh_token': tokens.refresh_token
            }

        # If the tokens are valid, return them in a dictionary format
        return {
            'access_token': tokens.access_token,
            'refresh_token': tokens.refresh_token
        }

    async def exchange_code_for_tokens(self, code: int, user_id: str, realm_id: str):
        try:
            # print(code, "code")
            self.auth_client.get_bearer_token(code)

            # print(test, "AUTHCODEE")
            access_token = self.auth_client.access_token
            refresh_token = self.auth_client.refresh_token
            print(realm_id, "realm_id !@##")

            print(user_id, "user_id")

            await self.repo.save_tokens(access_token, refresh_token, user_id, realm_id)

            # print(test, "test")
            return {"access_token": access_token, "refresh_token": refresh_token}
        except AuthClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def make_quickbooks_report_request(self, report_type, query_params: dict, access_token, user_id: str):
        print(user_id, "user_id6346")
        # if access_token:
        #     tokens = await self.refresh_access_token_if_needed(user_id)
        #     if not tokens:
        #         raise HTTPException(
        #             status_code=401, detail="Authentication required")
        #     token_to_use = tokens['access_token']

        company_id = await self.repo.get_realm_id_by_user_id(user_id)

        # print(token_to_use, "token_to_use")
        print(company_id, "company_id")

        if report_type != "Invoice":
            # url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/reports/{report_type}"
            url = f"https://quickbooks.api.intuit.com/v3/company/{company_id}/reports/{report_type}"
        elif report_type == "Invoice":

            sql_statement = "select * from Invoice"
            # sql_statement = "select * from Invoice where id = '130'"

            # url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/query?query={sql_statement}"
            url = f"https://quickbooks.api.intuit.com/v3/company/{company_id}/query?query={sql_statement}"

        else:
            pass
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            return response.json()

    def parse_cashflow_report(self, report_data):
        #  # Get the current directory of the quickbooks_service.py file
        #     current_directory = os.path.dirname(os.path.abspath(__file__))

        #     # Navigate from 'services' to the 'api' directory
        #     app_directory = os.path.dirname(os.path.dirname(current_directory))

        #     # Navigate from 'app' to the 'samples' directory
        #     samples_directory = os.path.join(app_directory, 'reportSamples')

        #     # Define the relative path to the JSON file inside the 'samples' directory
        #     json_file_path = os.path.join(samples_directory, 'CashFlow.json')

        # # Step 2: Open and read the JSON file
        #     with open(json_file_path, 'r') as json_file:
        #         report_data = json.load(json_file)
        #     # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {}).get('Column', [])
        rows = report_data.get('Rows', {})

        return {
            "Header": header,
            "Columns": columns,
            "Rows": rows
        }

    def parse_transaction_list_report(self, report_data):

        #     # Get the current directory of the quickbooks_service.py file
        #     current_directory = os.path.dirname(os.path.abspath(__file__))

        #     # Navigate from 'services' to the 'api' directory
        #     app_directory = os.path.dirname(os.path.dirname(current_directory))

        #     # Navigate from 'app' to the 'samples' directory
        #     samples_directory = os.path.join(app_directory, 'reportSamples')

        #     # Define the relative path to the JSON file inside the 'samples' directory
        #     json_file_path = os.path.join(
        #         samples_directory, 'TransactionList.json')

        # # Step 2: Open and read the JSON file
        #     with open(json_file_path, 'r') as json_file:
        #         report_data = json.load(json_file)
        # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {})

        # Extract rows and keep them in raw format
        rows = report_data.get('Rows', {})

        return {"Header": header, "Rows": rows, "Columns": columns}

    def parse_aged_payable_detail_report(self, report_data):

        #     # Get the current directory of the quickbooks_service.py file
        #     current_directory = os.path.dirname(os.path.abspath(__file__))

        #     # Navigate from 'services' to the 'api' directory
        #     app_directory = os.path.dirname(os.path.dirname(current_directory))

        #     # Navigate from 'app' to the 'samples' directory
        #     samples_directory = os.path.join(app_directory, 'reportSamples')

        #     # Define the relative path to the JSON file inside the 'samples' directory
        #     json_file_path = os.path.join(samples_directory, 'aPagingDetail.json')

        #     # Check if the file exists
        #     if os.path.exists(json_file_path):
        #         print(f"JSON file path: {json_file_path}")
        #     else:
        #         print("JSON file not found.")

        # # Step 2: Open and read the JSON file
        #     with open(json_file_path, 'r') as json_file:
        #         report_data = json.load(json_file)
        # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {})

        # Extract rows and keep them in raw format
        rows = report_data.get('Rows', {})

        return {"Header": header, "Rows": rows, "Columns": columns}

    def parse_balance_sheet_report(self, report_data):

        #     # Get the current directory of the quickbooks_service.py file
        #     current_directory = os.path.dirname(os.path.abspath(__file__))

        #     # Navigate from 'services' to the 'api' directory
        #     app_directory = os.path.dirname(os.path.dirname(current_directory))

        #     # Navigate from 'app' to the 'samples' directory
        #     samples_directory = os.path.join(app_directory, 'reportSamples')

        #     # Define the relative path to the JSON file inside the 'samples' directory
        #     json_file_path = os.path.join(samples_directory, 'BalanceSheet.json')

        #     # Check if the file exists
        #     if os.path.exists(json_file_path):
        #         print(f"JSON file path: {json_file_path}")
        #     else:
        #         print("JSON file not found.")

        # # Step 2: Open and read the JSON file
        #     with open(json_file_path, 'r') as json_file:
        #         report_data = json.load(json_file)
        # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {})

        # Extract rows and keep them in raw format
        rows = report_data.get('Rows', {})

        return {"Header": header, "Rows": rows, "Columns": columns}

    def parse_customer_balance_detail_list_report(self, report_data):

        #     # Get the current directory of the quickbooks_service.py file
        #     current_directory = os.path.dirname(os.path.abspath(__file__))

        #     # Navigate from 'services' to the 'api' directory
        #     app_directory = os.path.dirname(os.path.dirname(current_directory))

        #     # Navigate from 'app' to the 'samples' directory
        #     samples_directory = os.path.join(app_directory, 'reportSamples')

        #     # Define the relative path to the JSON file inside the 'samples' directory
        #     json_file_path = os.path.join(
        #         samples_directory, 'CustomerBalanceDetail.json')

        #     # Check if the file exists
        #     if os.path.exists(json_file_path):
        #         print(f"JSON file path: {json_file_path}")
        #     else:
        #         print("JSON file not found.")

        # # Step 2: Open and read the JSON file
        #     with open(json_file_path, 'r') as json_file:
        #         report_data = json.load(json_file)
        # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {})

        # Extract rows and keep them in raw format
        rows = report_data.get('Rows', {})

        return {"Header": header, "Rows": rows, "Columns": columns}

    def parse_invoice_report(self, report_data):

        #     # Get the current directory of the quickbooks_service.py file
        #     current_directory = os.path.dirname(os.path.abspath(__file__))

        #     # Navigate from 'services' to the 'api' directory
        #     app_directory = os.path.dirname(os.path.dirname(current_directory))

        #     # Navigate from 'app' to the 'samples' directory
        #     samples_directory = os.path.join(app_directory, 'reportSamples')

        #     # Define the relative path to the JSON file inside the 'samples' directory
        #     json_file_path = os.path.join(
        #         samples_directory, 'InvoiceQueryResponse.json')

        #     # Check if the file exists
        #     if os.path.exists(json_file_path):
        #         print(f"JSON file path: {json_file_path}")
        #     else:
        #         print("JSON file not found.")

        # # Step 2: Open and read the JSON file
        #     with open(json_file_path, 'r') as json_file:
        #         report_data = json.load(json_file)
        # Extract the header and columns
        queryResponse = report_data.get('QueryResponse', {})
        time = report_data.get('time', {})

        return {"QueryResponse": queryResponse, "Time": time}

    def parse_profit_and_loss_detail_report(self, report_data):

        #     # Get the current directory of the quickbooks_service.py file
        #     current_directory = os.path.dirname(os.path.abspath(__file__))

        #     # Navigate from 'services' to the 'api' directory
        #     app_directory = os.path.dirname(os.path.dirname(current_directory))

        #     # Navigate from 'app' to the 'samples' directory
        #     samples_directory = os.path.join(app_directory, 'reportSamples')

        #     # Define the relative path to the JSON file inside the 'samples' directory
        #     json_file_path = os.path.join(
        #         samples_directory, 'ProfitandLossDetail.json')

        #     # Check if the file exists
        #     if os.path.exists(json_file_path):
        #         print(f"JSON file path: {json_file_path}")
        #     else:
        #         print("JSON file not found.")

        # # Step 2: Open and read the JSON file
        #     with open(json_file_path, 'r') as json_file:
        #         report_data = json.load(json_file)
        # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {}).get('Column', [])
        rows = report_data.get('Rows', {})

        return {"Header": header, "Rows": rows, "Columns": columns}

    def parse_sales_by_product_report(self, report_data):

        # Get the current directory of the quickbooks_service.py file
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Navigate from 'services' to the 'api' directory
        app_directory = os.path.dirname(os.path.dirname(current_directory))

        # Navigate from 'app' to the 'samples' directory
        samples_directory = os.path.join(app_directory, 'reportSamples')

        # Define the relative path to the JSON file inside the 'samples' directory
        json_file_path = os.path.join(samples_directory, 'SalesByProduct.json')

        # Check if the file exists
        if os.path.exists(json_file_path):
            print(f"JSON file path: {json_file_path}")
        else:
            print("JSON file not found.")

    # Step 2: Open and read the JSON file
        with open(json_file_path, 'r') as json_file:
            report_data = json.load(json_file)
        # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {})

        # Extract rows and keep them in raw format
        rows = report_data.get('Rows', {})

        return {"Header": header, "Rows": rows, "Columns": columns}

    def parse_trial_balance_report(self, report_data):

        # Get the current directory of the quickbooks_service.py file
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Navigate from 'services' to the 'api' directory
        app_directory = os.path.dirname(os.path.dirname(current_directory))

        # Navigate from 'app' to the 'samples' directory
        samples_directory = os.path.join(app_directory, 'reportSamples')

        # Define the relative path to the JSON file inside the 'samples' directory
        json_file_path = os.path.join(samples_directory, 'TrialBalance.json')

        # Check if the file exists
        if os.path.exists(json_file_path):
            print(f"JSON file path: {json_file_path}")
        else:
            print("JSON file not found.")

    # Step 2: Open and read the JSON file
        with open(json_file_path, 'r') as json_file:
            report_data = json.load(json_file)
        # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {})

        # Extract rows and keep them in raw format
        rows = report_data.get('Rows', {})

        return {"Header": header, "Rows": rows, "Columns": columns}

    def parse_general_ledger_report(self, report_data):

        #     # Get the current directory of the quickbooks_service.py file
        #     current_directory = os.path.dirname(os.path.abspath(__file__))

        #     # Navigate from 'services' to the 'api' directory
        #     app_directory = os.path.dirname(os.path.dirname(current_directory))

        #     # Navigate from 'app' to the 'samples' directory
        #     samples_directory = os.path.join(app_directory, 'reportSamples')

        #     # Define the relative path to the JSON file inside the 'samples' directory
        #     json_file_path = os.path.join(samples_directory, 'GeneralLedger.json')

        #     # Check if the file exists
        #     if os.path.exists(json_file_path):
        #         print(f"JSON file path: {json_file_path}")
        #     else:
        #         print("JSON file not found.")

        # # Step 2: Open and read the JSON file
        #     with open(json_file_path, 'r') as json_file:
        #         report_data = json.load(json_file)
        # Extract the header and columns
        header = report_data.get('Header', {})
        columns = report_data.get('Columns', {})

        # Extract rows and keep them in raw format
        rows = report_data.get('Rows', {})

        return {"Header": header, "Rows": rows, "Columns": columns}

    def parse_quickbooks_report(self, report_data):
        # Check for 'QueryResponse' and 'Invoice' keys for invoice reports
        if 'QueryResponse' in report_data and 'time' in report_data:
            # Handle invoice report parsing
            return self.parse_invoice_report(report_data)
        elif 'Header' in report_data and 'ReportName' in report_data['Header']:
            # For other reports, check the 'header' for the report name
            report_name = report_data.get(
                'Header', {}).get('ReportName', '').lower()

            if report_name == 'cashflow':
                return self.parse_cashflow_report(report_data)
            elif report_name == 'transactionlist':
                return self.parse_transaction_list_report(report_data)
            elif report_name == 'agedpayabledetail':
                return self.parse_aged_payable_detail_report(report_data)
            elif report_name == 'balancesheet':
                return self.parse_balance_sheet_report(report_data)
            elif report_name == 'customerbalancedetail':
                return self.parse_customer_balance_detail_list_report(report_data)
            elif report_name == 'profitandlossdetail':
                return self.parse_profit_and_loss_detail_report(report_data)
            elif report_name == 'salesbyproduct':
                return self.parse_sales_by_product_report(report_data)
            elif report_name == 'trialbalance':
                return self.parse_trial_balance_report(report_data)
            elif report_name == 'generalledger':
                return self.parse_general_ledger_report(report_data)
            else:
                return {"message": "Unknown report type or no data available."}
        else:
            pass
