# dependencies.py

from app.api.services.azure_service import AzureBlobService
from app.config.aws_config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_S3_BUCKET_NAME  # Adjust the import path as needed


def get_aws_s3_service():
    # Initialize and configure your AWSS3Service instance here
    # Potentially use environment variables or other configuration methods
    aws_s3_service = AzureBlobService(
        access_key=AWS_ACCESS_KEY_ID,
        secret_key=AWS_SECRET_ACCESS_KEY,
        region=AWS_REGION,
        # endpoint_url="your_endpoint_url"
    )
    return aws_s3_service
