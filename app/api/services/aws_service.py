import boto3
import json
from fastapi import HTTPException
# Ensure correct import path
from app.config.aws_config import AWS_ACCESS_KEY_ID, AWS_ACCESS_KEY_ID, AWS_ENDPOINT_URL, AWS_REGION, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME


class AWSS3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=AWS_REGION,
            endpoint_url=AWS_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = AWS_S3_BUCKET_NAME

    async def upload_json_to_s3(self, object_name: str, data: dict):
        try:
            data_bytes = json.dumps(data).encode('UTF-8')

            print(f"Uploading {object_name} to {self.bucket_name}...")

            self.s3_client.put_object(
                Bucket=self.bucket_name, Key=object_name, Body=data_bytes)
            print(
                f"Successfully uploaded {object_name} to {self.bucket_name}.")
        except Exception as e:
            print(f"Failed to upload {object_name} to {self.bucket_name}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to upload {object_name} to {self.bucket_name}.")
