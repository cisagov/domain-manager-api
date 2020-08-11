"""Synchronize database script."""
# Standard Python Libraries
import logging
import os

# Third-Party Libraries
import boto3
from dotenv import load_dotenv
from namecheap import Api

# cisagov Libraries
import pymongo

load_dotenv()
logger = logging.getLogger()

WEBSITE_STORAGE_URL = os.environ.get("WEBSITE_STORAGE_URL")
CONN_STR = "mongodb://{}:{}@localhost:27016/".format(
    os.environ.get("DB_USER"), os.environ.get("DB_PW"),
)

client = pymongo.MongoClient(CONN_STR)

db = client.domain_management

# Initialize namecheap api client
nc_api = Api(
    ApiUser=os.environ.get("NC_USERNAME"),
    UserName=os.environ.get("NC_USERNAME"),
    ApiKey=os.environ.get("NC_API_KEY"),
    ClientIP=os.environ.get("NC_IP"),
    sandbox=False,
)


def load_s3():
    """Load the latest website data from s3 into the database."""
    db_sites = db.websites

    s3 = boto3.client("s3")

    # List websites within the S3 Repository
    websites = s3.list_objects(Bucket="con-pca-dev-websites")

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
    """Load the latest domain data from namecheap into the database."""
    db_domains = db.domains
    domain_load = [
        i
        for i in nc_api.domains_getList()
        if not db_domains.find_one({"Name": i.get("Name")})
    ]

    # Save latest data to the database
    if domain_load != []:
        db_domains.insert_many(domain_load)
        logger.info("Database has been synchronized with domain data.")


if __name__ == "__main__":
    load_domains()
    load_s3()
