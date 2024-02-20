# dependencies.py

from app.api.services.aws_service import AWSS3Service


def get_aws_s3_service():
    return AWSS3Service()


