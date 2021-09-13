"""Contains static vars to be used in application."""

# Standard Python Libraries
import logging
import os

# Third-Party Libraries
import mongomock

from .db import get_db

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dm-api")

# aws
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
os.environ["AWS_DEFAULT_REGION"] = AWS_REGION

# s3
TEMPLATE_BUCKET = os.environ["TEMPLATE_BUCKET"]
TEMPLATE_BUCKET_URL = f"{TEMPLATE_BUCKET}.s3-website-{AWS_REGION}.amazonaws.com"
WEBSITE_BUCKET = os.environ["WEBSITE_BUCKET"]
WEBSITE_BUCKET_URL = f"{WEBSITE_BUCKET}.s3-website-{AWS_REGION}.amazonaws.com"

# ses
SES_ASSUME_ROLE_ARN = os.environ.get("SES_ASSUME_ROLE_ARN")
SMTP_FROM = os.environ.get("SMTP_FROM")

# sqs
SQS_CATEGORIZE_URL = os.environ.get("SQS_CATEGORIZE_URL")
SQS_CHECK_CATEGORY_URL = os.environ.get("SQS_CHECK_CATEGORY_URL")

# cognito
COGNTIO_ENABLED = bool(int(os.environ.get("AWS_COGNITO_ENABLED", 0)))
COGNITO_DEFAULT_ADMIN = bool(int(os.environ.get("AWS_DEFAULT_USER_TO_ADMIN", 0)))
COGNITO_ADMIN_GROUP = os.environ.get("AWS_COGNITO_ADMIN_GROUP_NAME")
COGNITO_CLIENT_ID = os.environ.get("AWS_COGNITO_USER_POOL_CLIENT_ID")
COGNTIO_USER_POOL_ID = os.environ.get("AWS_COGNITO_USER_POOL_ID")

# static gen
STATIC_GEN_URL = os.environ.get("STATIC_GEN_URL")

if os.environ.get("PYTESTING"):
    DB = mongomock.MongoClient().db
else:
    DB = get_db()

# about
DEPLOYED_DATE = os.environ.get("DEPLOYED_DATE")
API_COMMIT_ID = os.environ.get("API_COMMIT_ID")
UI_COMMIT_ID = os.environ.get("UI_COMMIT_ID")
