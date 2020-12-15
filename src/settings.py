"""Contains static vars to be used in application."""

# Standard Python Libraries
import os

# Third-Party Libraries
from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder

# aws
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
TEMPLATE_BUCKET = os.environ["TEMPLATE_BUCKET"]
TEMPLATE_BUCKET_URL = f"http://{TEMPLATE_BUCKET}.s3-website-{AWS_REGION}.amazonaws.com/"

# static gen
STATIC_GEN_URL = os.environ.get("STATIC_GEN_URL")

# database
if os.environ.get("MONGO_TYPE", "MONGO") == "DOCUMENTDB":
    CONN_STR_FMT = "mongodb://{}:{}@{}:{}/?ssl=true&ssl_ca_certs=/var/www/rds-combined-ca-bundle.pem&retryWrites=false"
else:
    CONN_STR_FMT = "mongodb://{}:{}@{}:{}/"

if int(os.environ.get("USE_SSH", 0)) == 1:
    server = SSHTunnelForwarder(
        (os.environ.get("SSH_ADDRESS"), int(os.environ.get("SSH_PORT", 22))),
        ssh_username=os.environ.get("SSH_USERNAME"),
        ssh_pkey=os.environ.get("SSH_PRIVATE_KEY"),
        remote_bind_address=(
            os.environ.get("DB_HOST"),
            int(os.environ.get("DB_PORT", 27017)),
        ),
    )
    server.start()
    CONN_STR = CONN_STR_FMT.format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PW"),
        "127.0.0.1",
        server.local_bind_port,
    )
else:
    CONN_STR = CONN_STR_FMT.format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PW"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
    )

CLIENT = MongoClient(CONN_STR)

# Set project database
DB = CLIENT.domain_management
