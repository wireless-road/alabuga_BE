import os

import boto3


def configure_s3_client_():
    AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID = os.getenv(
        "AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID"
    )
    AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY = os.getenv(
        "AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY"
    )
    AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION = os.getenv(
        "AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION"
    )
    AWS_EMAIL_INBOUND_BUCKET = {
        "aws_access_key_id": AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY,
        "region_name": AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION,
    }
    s3 = boto3.client("s3", **AWS_EMAIL_INBOUND_BUCKET)
    return s3
