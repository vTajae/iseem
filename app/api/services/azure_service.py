from azure.storage.blob import BlobServiceClient, BlobClient
from app.utils.utils import get_env_variable


AZURE_CONNECTION_STRING = get_env_variable('AZURE_CONNECTION_STRING')
CONTAINER_NAME = get_env_variable('CONTAINER_NAME')
ACCOUNT_NAME = get_env_variable('ACCOUNT_NAME')
ACCOUNT_KEY = get_env_variable('ACCOUNT_KEY')


class AzureBlobService:
    def __init__(self, connection_string: str, container_name: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = container_name
        self.container_client = self.blob_service_client.get_container_client(container_name)

    async def upload_blob(self, blob_name: str, data: bytes):
        blob_client = self.container_client.get_blob_client(blob_name)
        await blob_client.upload_blob(data)

    async def create_blob_from_path(self, blob_name: str, file_path: str):
        with open(file_path, "rb") as data:
            await self.upload_blob(blob_name, data.read())

