"""Synchronize database script."""
# Standard Python Libraries
import logging
import os

# Third-Party Libraries
import boto3
from dotenv import load_dotenv
import pymongo

load_dotenv()
logger = logging.getLogger()

WEBSITE_STORAGE_URL = os.environ.get("WEBSITE_STORAGE_URL")
SOURCE_BUCKET = os.environ.get("SOURCE_BUCKET")


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

client = pymongo.MongoClient(CONN_STR)

db = client.domain_management

# Initialize AWS Clients
s3 = boto3.client("s3")
route53 = boto3.client("route53")


def load_s3():
    """Load the latest website data from s3 into the database."""
    db_sites = db.websites

    # List websites within the S3 Repository
    websites = s3.list_objects(Bucket=SOURCE_BUCKET)

    # Pull Available websites
    available_prefixes = {i.get("Key").split("/")[0] for i in websites.get("Contents")}

    # Create load data
    s3_load = [
        {"name": i, "url": WEBSITE_STORAGE_URL + i}
        for i in available_prefixes
        if not db_sites.find_one({"name": i})
    ]

    # Save latest data to the database
    if s3_load != []:
        db_sites.insert_many(s3_load)
        logger.info("Database has been synchronized with S3 data.")


def load_domains():
    """Load the latest domain data from route53 into the database."""
    db_domains = db.domains
    domain_load = route53.list_hosted_zones().get("HostedZones")

    # Save latest data to the database
    if domain_load != []:
        db_domains.insert_many(domain_load)
        logger.info("Database has been synchronized with domain data.")


def lambda_handler(event, context):
    """Lambda handler."""
    load_domains()
    load_s3()


if __name__ == "__main__":
    load_domains()
    load_s3()
