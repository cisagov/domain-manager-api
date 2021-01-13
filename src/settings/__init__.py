"""Contains static vars to be used in application."""

# Standard Python Libraries
import os

# Third-Party Libraries
import mongomock

from .db_settings import get_db

# aws
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
os.environ["AWS_DEFAULT_REGION"] = AWS_REGION
TEMPLATE_BUCKET = os.environ["TEMPLATE_BUCKET"]
TEMPLATE_BUCKET_URL = f"{TEMPLATE_BUCKET}.s3-website-{AWS_REGION}.amazonaws.com"
WEBSITE_BUCKET = os.environ["WEBSITE_BUCKET"]
WEBSITE_BUCKET_URL = f"{WEBSITE_BUCKET}.s3-website-{AWS_REGION}.amazonaws.com"

# static gen
STATIC_GEN_URL = os.environ.get("STATIC_GEN_URL")

if os.environ.get("PYTESTING"):
    DB = mongomock.MongoClient().db
else:
    DB = get_db()
