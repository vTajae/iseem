# services/azure_blob_service.py
import json
from fastapi import HTTPException
from app.config.azure_config import blob_service_client

class AzureBlobService:
    def __init__(self, container_name, account_name, account_key):
        
        self.blob_service_client = BlobServiceClient(
            container_name=container_name,
            account_name=account_name,
            account_key=account_key,
        )
        

    async def upload_blob(self, blob_name: str, data: dict):
        try:
            blob_client = self.blob_service_client.ge(container=self.container_name, blob=blob_name)
            data_bytes = json.dumps(data).encode('utf-8')
            await blob_client.upload_blob(data_bytes, overwrite=True)
            print(f"Blob {blob_name} uploaded to container {self.container_name}.")
        except Exception as e:
            print(f"Failed to upload blob: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload blob.")