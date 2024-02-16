# config.py
from dotenv import load_dotenv
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

from app.utils.utils import empty_to_none, get_env_variable

# Load environment variables from .env file
load_dotenv()

# # QuickBooks Configuration
QUICKBOOKS_CLIENT_ID = get_env_variable('QUICKBOOKS_CLIENT_ID')
QUICKBOOKS_SECRET = get_env_variable('QUICKBOOKS_SECRET')
QUICKBOOKS_ENV = get_env_variable('QUICKBOOKS_ENV')
QUICKBOOKS_REDIRECT_URI = get_env_variable('QUICKBOOKS_REDIRECT_URI')

# QuickBooks Configuration
# QUICKBOOKS_CLIENT_ID = get_env_variable('PROD_QUICKBOOKS_CLIENT_ID')
# QUICKBOOKS_SECRET = get_env_variable('PROD_QUICKBOOKS_SECRET')
# QUICKBOOKS_ENV = get_env_variable('PROD_QUICKBOOKS_ENV')
# QUICKBOOKS_REDIRECT_URI = get_env_variable('PROD_QUICKBOOKS_REDIRECT_URI')

# Initialize the AuthClient for QuickBooks
auth_client = AuthClient(
    client_id=QUICKBOOKS_CLIENT_ID,
    client_secret=QUICKBOOKS_SECRET,
    environment=QUICKBOOKS_ENV,
    redirect_uri=QUICKBOOKS_REDIRECT_URI
)

# Scopes
QUICKBOOKS_SCOPES = [Scopes.ACCOUNTING, Scopes.PAYMENT]
auth_url = auth_client.get_authorization_url(QUICKBOOKS_SCOPES)
