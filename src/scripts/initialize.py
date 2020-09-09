"""Initialize database script."""
# Standard Python Libraries
from datetime import datetime
import logging
import json
import os

# Third-Party Libraries
import boto3
import pymongo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


WEBSITE_STORAGE_URL = os.environ.get("WEBSITE_STORAGE_URL")
SOURCE_BUCKET = os.environ.get("SOURCE_BUCKET")


if os.environ.get("MONGO_TYPE", "MONGO") == "DOCUMENTDB":
    CONN_STR = "mongodb://{}:{}@{}:{}/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&retryWrites=false".format(
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


def load_file(data_file):
    """Load json files."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, data_file)
    with open(data_file, "r") as f:
        data = json.load(f)
    return data


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

    domain_list = [
        domain
        for domain in domain_load
        if not db_domains.find_one({"Name": domain.get("Name")})
    ]

    # Save latest data to the database
    if domain_list != []:
        db_domains.insert_many(domain_list)
        logger.info("Database has been synchronized with domain data.")


def load_applications():
    """Load dummy application data to the database."""
    db_applications = db.applications

    application_json = load_file("data/applications.json")

    application_data = []
    for application in application_json:
        if not db_applications.find_one({"name": application.get("name")}):
            application["requested_date"] = datetime.utcnow()
            application_data.append(application)

    # Save latest data to the database
    if application_data != []:
        db_applications.insert_many(application_data)
        return logger.info("Application data has been loaded into the database.")


if __name__ == "__main__":
    load_domains()
    load_s3()
    load_applications()
    logger.info("Database has been initialized.")
