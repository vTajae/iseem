# settings.py
from dotenv import load_dotenv
from plaid.api import plaid_api
from plaid.configuration import Configuration, Environment
import plaid
from plaid.api_client import ApiClient

from app.utils.utils import empty_to_none, get_env_variable

load_dotenv()

# Fill in your Plaid API keys
PLAID_CLIENT_ID = get_env_variable('PLAID_CLIENT_ID')
PLAID_SECRET = get_env_variable('PLAID_SANDBOX_SECRET')
PLAID_ENV = get_env_variable('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = get_env_variable('PLAID_PRODUCTS', 'transactions').split(',')
PLAID_COUNTRY_CODES = get_env_variable('PLAID_COUNTRY_CODES', 'US').split(',')
PLAID_VERSION = get_env_variable('PLAID_VERSION')
# Determine the appropriate environment
if PLAID_ENV == 'development':
    host = Environment.Development
elif PLAID_ENV == 'production':
    host = Environment.Production
else:
    host = Environment.Sandbox

PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')

# Initialize the Plaid client
configuration = Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': PLAID_VERSION
    }
)

api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)