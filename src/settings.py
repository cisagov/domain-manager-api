"""Contains static vars to be used in application."""

import os

# Third-Party Libraries
from pymongo import MongoClient


# aws
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
TEMPLATE_BUCKET = os.environ["TEMPLATE_BUCKET"]
TEMPLATE_BUCKET_URL = f"http://{TEMPLATE_BUCKET}.s3-website-{AWS_REGION}.amazonaws.com/"

# database
if os.environ.get("MONGO_TYPE", "MONGO") == "DOCUMENTDB":
    CONN_STR = "mongodb://{}:{}@{}:{}/?ssl=true&ssl_ca_certs=/var/www/rds-combined-ca-bundle.pem&retryWrites=false".format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PW"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
    )

else:
    CONN_STR = "mongodb://{}:{}@{}:{}/".format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PW"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
    )

CLIENT = MongoClient(CONN_STR)

# Set project database
DB = CLIENT.domain_management
