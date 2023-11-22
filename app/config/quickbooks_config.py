# settings.py
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes


# Function to get environment variables
def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if default is None and value is None:
        raise HTTPException(status_code=500, detail=f"Environment variable {var_name} not set")
    return value

# Function to convert empty strings to None
def empty_to_none(field):
    value = os.getenv(field)
    return None if value is None or len(value) == 0 else value

# Load environment variables from .env file
load_dotenv()

# QuickBooks API Keys
QUICKBOOKS_CLIENT_ID = get_env_variable('QUICKBOOKS_CLIENT_ID')
QUICKBOOKS_SECRET = get_env_variable('QUICKBOOKS_SECRET')

# QuickBooks Environment ('sandbox', 'development', or 'production')
QUICKBOOKS_ENV = get_env_variable('QUICKBOOKS_ENV')

# QuickBooks Redirect URI
QUICKBOOKS_REDIRECT_URI = empty_to_none('QUICKBOOKS_REDIRECT_URI')


# Initialize the AuthClient for QuickBooks
auth_client = AuthClient(
    client_id=QUICKBOOKS_CLIENT_ID,
    client_secret=QUICKBOOKS_SECRET,
    environment=QUICKBOOKS_ENV,
    redirect_uri=QUICKBOOKS_REDIRECT_URI
)

scopes_string = get_env_variable('QUICKBOOKS_SCOPES')

scopes_map = {
    'ACCOUNTING': Scopes.ACCOUNTING,
    'PAYMENT': Scopes.PAYMENT,
}

QUICKBOOKS_SCOPES = [Scopes.ACCOUNTING, Scopes.PAYMENT]

auth_url = auth_client.get_authorization_url(QUICKBOOKS_SCOPES)
