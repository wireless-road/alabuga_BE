import os
import logging
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from flask import current_app as app
import hashlib
import io
from elar import s3_client
# from lxml import etree
import requests
import urllib
import ast

logger = logging.getLogger(__name__)


def store_file_to_s3_bucket(file_body, file_name, content_type, sub_folder=None):
    file_object = io.BytesIO(file_body)

    s3 = boto3.client("s3", **app.config["AWS"])
    region_name = app.config["AWS"]["region_name"]
    bucket_name = app.config["UPLOAD_DOC_S3_BUCKET"]

    hasher = hashlib.sha256()
    while chunk := file_object.read(8192):
        hasher.update(chunk)
    hash_val = hasher.hexdigest()

    file_object.seek(0)

    filename, file_extension = os.path.splitext(file_name)
    if sub_folder is None:
        obj_key = "{}{}".format(hash_val, file_extension)
    else:
        obj_key = "{}/{}{}".format(sub_folder, hash_val, file_extension)

    s3.put_object(
        Body=file_object.read(),
        Bucket=bucket_name,
        Key=obj_key,
        # ServerSideEncryption='aws:kms',
        ContentType=content_type,
    )
    object_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{obj_key}"
    return obj_key, object_url


def configure_s3_client():
    AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID = os.getenv('AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID')
    AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY = os.getenv('AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY')
    AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION = os.getenv('AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION')
    AWS_EMAIL_INBOUND_BUCKET = {
        'aws_access_key_id': AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID,
        'aws_secret_access_key': AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY,
        'region_name': AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION
    }
    s3 = boto3.client('s3', **AWS_EMAIL_INBOUND_BUCKET)
    return s3


def configure_s3_client_signature_version_4():
    AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID = os.getenv('AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID')
    AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY = os.getenv('AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY')
    AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION = os.getenv('AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION')
    AWS_EMAIL_INBOUND_BUCKET = {
        'aws_access_key_id': AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID,
        'aws_secret_access_key': AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY,
        'region_name': AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION
    }
    config = Config(
        signature_version='s3v4',
    )
    s3 = boto3.client('s3', **AWS_EMAIL_INBOUND_BUCKET, config=config)
    return s3


def configure_s3_resource():
    AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID = os.getenv('AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID')
    AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY = os.getenv('AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY')
    AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION = os.getenv('AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION')
    AWS_EMAIL_INBOUND_BUCKET = {
        'aws_access_key_id': AWS_EMAIL_INBOUND_BUCKET_ACCESS_KEY_ID,
        'aws_secret_access_key': AWS_EMAIL_INBOUND_BUCKET_SECRET_ACCESS_KEY,
        'region_name': AWS_EMAIL_INBOUND_BUCKET_DEFAULT_REGION
    }
    s3 = boto3.resource('s3', **AWS_EMAIL_INBOUND_BUCKET)
    return s3


def create_presigned_url(bucket_name, object_name, expiration=3600, SSECustomerAlgorithm=None):
    """
    Taken from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
    """
    try:
        params = {'Bucket': bucket_name, 'Key': object_name}
        if SSECustomerAlgorithm:
            params['SSECustomerAlgorithm'] = SSECustomerAlgorithm

        response = s3_client.generate_presigned_url('get_object',
                                                    Params=params,
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None
    # The response contains the presigned URL
    return response


def create_presigned_url_signature_version_4(bucket_name, object_name, expiration=3600, SSECustomerAlgorithm=None):
    """
    Taken from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
    """
    s3_client = configure_s3_client_signature_version_4()

    try:
        params = {'Bucket': bucket_name, 'Key': object_name}
        if SSECustomerAlgorithm:
            params['SSECustomerAlgorithm'] = SSECustomerAlgorithm

        response = s3_client.generate_presigned_url('get_object',
                                                    Params=params,
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None
    # The response contains the presigned URL
    return response


# ###################################################################
# ## SQS handling using AWS library
# ###################################################################
def sqs_receive_message_2():
    sqs = boto3.client('sqs', **app.config['AWS_SQS'])

    response = sqs.list_queues()
    queue_url = app.config['AWS_SQS_QUEUE_URL']

    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=['All'],
        VisibilityTimeout=60,
        WaitTimeSeconds=5
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    return response, status_code


def sqs_delete_message_2(receipt_handle):
    sqs = boto3.client('sqs', **app.config['AWS_SQS'])
    queue_url = app.config['AWS_SQS_QUEUE_URL']
    response = sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    logger.info(f'Email task. AWS sqs deletion message result: {response}')
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    return response, status_code


def sqs_parse_received_message_2(responce):
    message = responce['Messages'][0]

    receipt_handle = message['ReceiptHandle']
    body = message['Body']
    body_jsoned = ast.literal_eval(body)
    bucket_name = body_jsoned['Records'][0]['s3']['bucket']['name']
    file_key = body_jsoned['Records'][0]['s3']['object']['key']
    return receipt_handle, bucket_name, file_key


# ###################################################################
# ## SQS handling raw http queries. Deprecated. Don't use it.
# ###################################################################
def sqs_receive_message_():
    IAM_user = app.config['AWS_SQS_QUEUE_IAM_USER']
    s3_queue = app.config['AWS_SQS_QUEUE_NAME']
    action = 'ReceiveMessage'
    attributes_to_show = 'All'
    visibility_timeout = '60'
    wait_time_seconds = '5'
    url = 'https://sqs.eu-west-1.amazonaws.com/' + IAM_user + '/' + s3_queue \
          + '?Action=' + action \
          + '&AttributeName=' + attributes_to_show \
          + '&VisibilityTimeout=' + visibility_timeout \
          + '&WaitTimeSeconds=' + wait_time_seconds
    logger.info(f'___ url: {url}')
    responce = requests.get(url)
    res = responce.content
    status_code = responce.status_code
    return res, status_code


# def sqs_parse_received_message(responce):
#     root = etree.fromstring(responce)
#     node = root.xpath("//*[local-name() = 'ReceiptHandle']")[0]
#     receipt_handle = node.xpath("string()")
#     node = root.xpath("//*[local-name() = 'Body']")[0]
#     body = node.xpath("string()")
#     body_jsoned = ast.literal_eval(body)
#     bucket_name = body_jsoned['Records'][0]['s3']['bucket']['name']
#     file_key = body_jsoned['Records'][0]['s3']['object']['key']
#     return receipt_handle, bucket_name, file_key


def sqs_delete_message_(receipt_handle):
    IAM_user = app.config['AWS_SQS_QUEUE_IAM_USER']
    s3_queue = app.config['AWS_SQS_QUEUE_NAME']
    action = 'DeleteMessage'
    receipt_handle_encoded = urllib.parse.quote(receipt_handle)
    url = 'https://sqs.eu-west-1.amazonaws.com/' + IAM_user + '/' + s3_queue \
          + '?Action=' + action \
          + '&ReceiptHandle=' + receipt_handle_encoded
    responce = requests.get(url)
    res = responce.content
    status_code = responce.status_code
    return res, status_code
