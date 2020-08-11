"""Synchronize database script."""
import os
import logging

# Third-Party Libraries
import boto3
import pymongo
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger()

WEBSITE_STORAGE_URL = os.environ.get("WEBSITE_STORAGE_URL")
CONN_STR = "mongodb://{}:{}@localhost:27016/".format(
    os.environ.get("DB_USER"), os.environ.get("DB_PW"),
)

client = pymongo.MongoClient(CONN_STR)

db = client.domain_management


def load_s3():
    """Load the latest website data from s3 into the database."""
    db_sites = db.websites

    s3 = boto3.client("s3")

    # List websites within the S3 Repository
    websites = s3.list_objects(Bucket="con-pca-dev-websites")

    # Pull Available websites
    available_prefixes = set(
        [i.get("Key").split("/")[0] for i in websites.get("Contents")]
    )

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


load_s3()
