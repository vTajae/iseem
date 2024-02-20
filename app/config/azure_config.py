# config.py
from dotenv import load_dotenv
from azure.storage.blob.aio import BlobServiceClient

from app.utils.utils import get_env_variable

# Load environment variables from .env file
load_dotenv()

# Azure Configuration

CONTAINER_NAME = get_env_variable('CONTAINER_NAME')
ACCOUNT_NAME = get_env_variable('ACCOUNT_NAME')
ACCOUNT_KEY = get_env_variable('ACCOUNT_KEY')
AZURE_STORAGE_CONNECTION_STRING = get_env_variable('AZURE_STORAGE_CONNECTION_STRING')

# Initialize the AuthClient for Azure
blob_client = BlobServiceClient(
    container_name=CONTAINER_NAME,
    account_name=ACCOUNT_NAME,
    account_key=ACCOUNT_KEY,
)